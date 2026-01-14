"use client";

import { useEffect, useState } from "react";
import Visualization from "../components/Visualization";
import AnimationEditor from "../components/AnimationEditor";
import LayoutEditor from "../components/LayoutEditor";
import Image from "next/image";

export default function Home() {
    const [currentView, setCurrentView] = useState("viz");
    const [config, setConfig] = useState(null);
    const [rawConfigString, setRawConfigString] = useState(""); // Still needed for save functionality, even if tab is gone
    const [animations, setAnimations] = useState([]);
    // layoutConfig state removed — using `config` as the single source of truth
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);

    // Initial Fetch
    useEffect(() => {
        const fetchData = async () => {
            try {
                const [configRes, animRes] = await Promise.all([
                    fetch("/api/config/"),
                    fetch("/api/animations/"),
                ]);
                const configData = await configRes.json();
                const animData = await animRes.json();

                setConfig(configData);
                setRawConfigString(JSON.stringify(configData, null, 2));
                setAnimations(animData);
                setLoading(false);
            } catch (e) {
                console.error("Failed to load data", e);
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    // Update logic for Animation Editor
    const updateIdleConfig = (newVal) => {
        const newConfig = {
            ...config,
            animations: { ...config.animations, idle: newVal },
        };
        setConfig(newConfig);
        setRawConfigString(JSON.stringify(newConfig, null, 2));
    };

    const updateObjectConfig = (newVal) => {
        const newConfig = {
            ...config,
            animations: { ...config.animations, object: newVal },
        };
        setConfig(newConfig);
        setRawConfigString(JSON.stringify(newConfig, null, 2));
    };

    // Update logic for Strips & Floor Editor (mapped into `config`)
    const updateLayoutConfig = (newVal) => {
        const currentFloor = config?.projection?.floor || [0, 0, 0, 0];
        const newConfig = {
            ...config,
            strips: newVal.strips,
            projection: {
                ...config.projection,
                floor: [
                    currentFloor[0] ?? 0,
                    currentFloor[1] ?? 0,
                    parseFloat(newVal.floor?.width ?? 0),
                    parseFloat(newVal.floor?.height ?? 0),
                ],
            },
        };
        setConfig(newConfig);
        setRawConfigString(JSON.stringify(newConfig, null, 2));
    };

    const saveConfig = async () => {
        setSaving(true);
        try {
            // Save combined config (animations, strips, and projection.floor)
            const configRes = await fetch("/api/config/", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(config),
            });
            if (!configRes.ok) throw new Error("Failed to save config");

            // Reload config to confirm
            const newConfigRes = await fetch("/api/config/");
            const newConfig = await newConfigRes.json();

            setConfig(newConfig);
            setRawConfigString(JSON.stringify(newConfig, null, 2));
            alert("Configuration saved successfully!");
        } catch (e) {
            alert("Error saving configuration: " + e.message);
        } finally {
            setSaving(false);
        }
    };

    const resetConfig = async () => {
        if (!confirm("Are you sure you want to discard unsaved changes?"))
            return;
        const configRes = await fetch("/api/config/");
        const configData = await configRes.json();

        setConfig(configData);
        setRawConfigString(JSON.stringify(configData, null, 2));
    };

    if (loading) {
        return (
            <div className="h-screen flex items-center justify-center bg-gray-900 text-teal-400">
                Loading...
            </div>
        );
    }

    if (!config) {
        return (
            <div className="h-screen flex items-center justify-center bg-gray-900 text-red-400">
                Failed to load configuration.
            </div>
        );
    }

    return (
        <div className="flex flex-col h-screen bg-gray-900 text-gray-100">
            {/* Header */}
            <header className="bg-gray-800 border-b border-gray-700 p-4 flex items-center justify-between shrink-0">
                {/* Logo */}
                <div className="w-40 h-auto">
                    <Image
                        src="data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiIHN0YW5kYWxvbmU9Im5vIj8+CjwhLS0gQ3JlYXRlZCB3aXRoIElua3NjYXBlIChodHRwOi8vd3d3Lmlua3NjYXBlLm9yZy8pIC0tPgoKPHN2ZwogICB3aWR0aD0iMjA0OG1tIgogICBoZWlnaHQ9IjUxMm1tIgogICB2aWV3Qm94PSIwIDAgMjA0OCA1MTIiCiAgIHZlcnNpb249IjEuMSIKICAgaWQ9InN2ZzEiCiAgIHhtbDpzcGFjZT0icHJlc2VydmUiCiAgIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIKICAgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGRlZnMKICAgICBpZD0iZGVmczEiIC8+PGcKICAgICBpZD0ibGF5ZXIyIj48ZwogICAgICAgaWQ9ImcxIgogICAgICAgc3R5bGU9ImZpbGw6I2ZmZmZmZjtmaWxsLW9wYWNpdHk6MSI+PHRleHQKICAgICAgICAgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIKICAgICAgICAgc3R5bGU9ImZvbnQtd2VpZ2h0OjkwMDtmb250LXNpemU6MjgyLjIyMnB4O2ZvbnQtZmFtaWx5OlBvcHBpbnM7LWlua3NjYXBlLWZvbnQtc3BlY2lmaWNhdGlvbjonUG9wcGlucywgSGVhdnknO3RleHQtYWxpZ246c3RhcnQ7bGV0dGVyLXNwYWNpbmc6MHB4O3dyaXRpbmctbW9kZTpsci10YjtkaXJlY3Rpb246bHRyO3RleHQtYW5jaG9yOnN0YXJ0O2ZpbGw6I2ZmZmZmZjtmaWxsLW9wYWNpdHk6MTtzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6MS4wNTgzMztzdHJva2UtbGluZWNhcDpyb3VuZDtzdHJva2UtbGluZWpvaW46cm91bmQ7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgICAgeD0iMjQyLjMzNjkxIgogICAgICAgICB5PSI0NzcuMTMyNjYiCiAgICAgICAgIGlkPSJ0ZXh0MSI+PHRzcGFuCiAgICAgICAgICAgaWQ9InRzcGFuMSIKICAgICAgICAgICBzdHlsZT0iZm9udC1zaXplOjI4Mi4yMjJweDtzdHJva2Utd2lkdGg6MS4wNTgzMztmaWxsOiNmZmZmZmY7ZmlsbC1vcGFjaXR5OjEiCiAgICAgICAgICAgeD0iMjQyLjMzNjkxIgogICAgICAgICAgIHk9IjQ3Ny4xMzI2NiI+TUFLRVJTPC90c3Bhbj48L3RleHQ+PHRleHQKICAgICAgICAgeG1sOnNwYWNlPSJwcmVzZXJ2ZSIKICAgICAgICAgc3R5bGU9ImZvbnQtd2VpZ2h0OjkwMDtmb250LXNpemU6MjgyLjIyMnB4O2ZvbnQtZmFtaWx5OlBvcHBpbnM7LWlua3NjYXBlLWZvbnQtc3BlY2lmaWNhdGlvbjonUG9wcGlucywgSGVhdnknO3RleHQtYWxpZ246c3RhcnQ7bGV0dGVyLXNwYWNpbmc6MHB4O3dyaXRpbmctbW9kZTpsci10YjtkaXJlY3Rpb246bHRyO3RleHQtYW5jaG9yOnN0YXJ0O2ZpbGw6I2ZmZmZmZjtmaWxsLW9wYWNpdHk6MTtzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6MS4wNTgzMztzdHJva2UtbGluZWNhcDpyb3VuZDtzdHJva2UtbGluZWpvaW46cm91bmQ7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgICAgeD0iNTAxLjk4MTI5IgogICAgICAgICB5PSIyMzguMTU5MjMiCiAgICAgICAgIGlkPSJ0ZXh0MS01Ij48dHNwYW4KICAgICAgICAgICBpZD0idHNwYW4xLTMiCiAgICAgICAgICAgc3R5bGU9ImZvbnQtc2l6ZToyODIuMjIycHg7c3Ryb2tlLXdpZHRoOjEuMDU4MzM7ZmlsbDojZmZmZmZmO2ZpbGwtb3BhY2l0eToxIgogICAgICAgICAgIHg9IjUwMS45ODEyOSIKICAgICAgICAgICB5PSIyMzguMTU5MjMiPlNUVVBBPC90c3Bhbj48L3RleHQ+PC9nPjxnCiAgICAgICBpZD0ibGF5ZXIxLTQiCiAgICAgICB0cmFuc2Zvcm09InRyYW5zbGF0ZSgxNTM2KSI+PGcKICAgICAgICAgaWQ9ImcxMS03LTAtMC05LTAtMjAtNyIKICAgICAgICAgdHJhbnNmb3JtPSJtYXRyaXgoMCwwLjU5NjY3MTI1LDAuNTk2NjcxMjUsMCwzOTMuMjY3MywxNjEuODcwMDgpIgogICAgICAgICBzdHlsZT0ic3Ryb2tlLXdpZHRoOjAuNDQzNDMyIj48cGF0aAogICAgICAgICAgIGlkPSJwYXRoMy05LTMtMy04LTctMC0xLTAtMy0yLTgiCiAgICAgICAgICAgc3R5bGU9ImZpbGw6I2ZmY2MwMDtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6NS44NzYzNztzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgICAgICBkPSJtIDcyLjE4NzE0NSwtNjA4LjYzNDU1IGMgLTguMzg5MzY5LDM4LjQ0NDA2IC0yNy4yODIwOTMsNzAuODM0NDIgLTU0LjE3ODUyMSw5NC42MTM1MiAtNC4xMzcwMTksMy42NTc1NCAtNS40NDk4NDIsMTAuMjY5NTEgLTIuNjg4NTQ4LDE1LjA1MjUxIDE0LjY3NTkzOCwyNS40MjEwNyAyOS4zNTE4NzcsNTAuODQyMTQgNDQuMDI3ODE2LDc2LjI2MzIxIDIuNzYxMjkzLDQuNzgzIDguNjczNTU5LDYuMDk4MiAxMy4wNjg2NzMsMi43NTQzNSAyOC41NDgzNDUsLTIxLjcxOTg4IDUyLjUxMDcyNSwtNDguOTU3NjMgNzIuMDEzODc1LC04MS43NjU1MyAyLjgyMjA0LC00Ljc0NzE4IDMuMDA0NTgsLTEyLjY5MDYgMC43Mjg0LC0xNy43MjE4NSAtNy4xMTEwMywtMTUuNzE4MTMgLTIxLjA5MDk4LC01MC4xMzA1MiAtMjUuNjg2MjQsLTg5LjA2MTE2IC0wLjY0NzM1LC01LjQ4NDI3IC01LjQzMDk1LC05Ljk1MzUxIC0xMC45NTM4LC05Ljk1MzUzIGwgLTI0LjQ0MDY3NSwtNmUtNSBjIC01LjUyMjg0NywtMmUtNSAtMTAuNzEzNTk4LDQuNDIzMjEgLTExLjg5MDk4LDkuODE4NTQgeiIgLz48cGF0aAogICAgICAgICAgIGlkPSJwYXRoMy05LTMtMy04LTctMy0xLTctMy02LTMtNCIKICAgICAgICAgICBzdHlsZT0iZmlsbDojZjE4NzAwO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lO3N0cm9rZS13aWR0aDo1Ljg3NjM3O3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgICAgIGQ9Im0gNzIuMTg3MTQ1LC02MDguNjM0NTUgYyAtOC4zODkzNjksMzguNDQ0MDYgLTI3LjI4MjA5Myw3MC44MzQ0MiAtNTQuMTc4NTIxLDk0LjYxMzUyIC00LjEzNzAxOSwzLjY1NzU0IC01LjQ0OTg0MiwxMC4yNjk1MSAtMi42ODg1NDgsMTUuMDUyNTEgMTQuNjc1OTM4LDI1LjQyMTA3IDI5LjM1MTg3Nyw1MC44NDIxNCA0NC4wMjc4MTYsNzYuMjYzMjEgMi43NjEyOTMsNC43ODMgOC42NzM1NTksNi4wOTgyIDEzLjA2ODY3MywyLjc1NDM1IDI4LjU0ODM0NSwtMjEuNzE5ODggNTIuNTEwNzI1LC00OC45NTc2MyA3Mi4wMTM4NzUsLTgxLjc2NTUzIDIuODIyMDQsLTQuNzQ3MTggMy4wMDQ1OCwtMTIuNjkwNiAwLjcyODQsLTE3LjcyMTg1IC03LjExMTAzLC0xNS43MTgxMyAtMjEuMDkwOTgsLTUwLjEzMDUyIC0yNS42ODYyNCwtODkuMDYxMTYgLTAuNjQ3MzUsLTUuNDg0MjcgLTUuNDMwOTUsLTkuOTUzNTEgLTEwLjk1MzgsLTkuOTUzNTMgbCAtMjQuNDQwNjc1LC02ZS01IGMgLTUuNTIyODQ3LC0yZS01IC0xMC43MTM1OTgsNC40MjMyMSAtMTEuODkwOTgsOS44MTg1NCB6IgogICAgICAgICAgIHRyYW5zZm9ybT0icm90YXRlKDEyMCwxNTguNDY0NywtNDk1Ljk4Mjc1KSIgLz48cGF0aAogICAgICAgICAgIGlkPSJwYXRoMy05LTMtMy04LTctMy01LTItOS0zLTItNy01IgogICAgICAgICAgIHN0eWxlPSJmaWxsOiNjZTE2MjU7ZmlsbC1vcGFjaXR5OjE7ZmlsbC1ydWxlOm5vbnplcm87c3Ryb2tlOm5vbmU7c3Ryb2tlLXdpZHRoOjUuODc2Mzc7c3Ryb2tlLWRhc2hhcnJheTpub25lO3N0cm9rZS1vcGFjaXR5OjEiCiAgICAgICAgICAgZD0ibSA3Mi4xODcxNDUsLTYwOC42MzQ1NSBjIC04LjM4OTM2OSwzOC40NDQwNiAtMjcuMjgyMDkzLDcwLjgzNDQyIC01NC4xNzg1MjEsOTQuNjEzNTIgLTQuMTM3MDE5LDMuNjU3NTQgLTUuNDQ5ODQyLDEwLjI2OTUxIC0yLjY4ODU0OCwxNS4wNTI1MSAxNC42NzU5MzgsMjUuNDIxMDcgMjkuMzUxODc3LDUwLjg0MjE0IDQ0LjAyNzgxNiw3Ni4yNjMyMSAyLjc2MTI5Myw0Ljc4MyA4LjY3MzU1OSw2LjA5ODIgMTMuMDY4NjczLDIuNzU0MzUgMjguNTQ4MzQ1LC0yMS43MTk4OCA1Mi41MTA3MjUsLTQ4Ljk1NzYzIDcyLjAxMzg3NSwtODEuNzY1NTMgMi44MjIwNCwtNC43NDcxOCAzLjAwNDU4LC0xMi42OTA2IDAuNzI4NCwtMTcuNzIxODUgLTcuMTExMDMsLTE1LjcxODEzIC0yMS4wOTA5OCwtNTAuMTMwNTIgLTI1LjY4NjI0LC04OS4wNjExNiAtMC42NDczNSwtNS40ODQyNyAtNS40MzA5NSwtOS45NTM1MSAtMTAuOTUzOCwtOS45NTM1MyBsIC0yNC40NDA2NzUsLTZlLTUgYyAtNS41MjI4NDcsLTJlLTUgLTEwLjcxMzU5OCw0LjQyMzIxIC0xMS44OTA5OCw5LjgxODU0IHoiCiAgICAgICAgICAgdHJhbnNmb3JtPSJyb3RhdGUoLTEyMCwxNTguNDU0MTUsLTQ5NS45OTEyMikiIC8+PC9nPjxnCiAgICAgICAgIGlkPSJnMTEtNy0wLTAtOS0wLTAtNS0wIgogICAgICAgICB0cmFuc2Zvcm09Im1hdHJpeCgwLjUxNjczMjQ2LC0wLjI5ODMzNTYyLDAuMjk4MzM1NjIsMC41MTY3MzI0NiwyNDEuOTU0NjgsNDIzLjkzNTczKSIKICAgICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDowLjQ0MzQzMiI+PHBhdGgKICAgICAgICAgICBpZD0icGF0aDMtOS0zLTMtOC03LTAtMS0wLTMtMS05LTMiCiAgICAgICAgICAgc3R5bGU9ImZpbGw6IzAwOGI5MjtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6NS44NzYzNztzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgICAgICBkPSJtIDcyLjE4NzE0NSwtNjA4LjYzNDU1IGMgLTguMzg5MzY5LDM4LjQ0NDA2IC0yNy4yODIwOTMsNzAuODM0NDIgLTU0LjE3ODUyMSw5NC42MTM1MiAtNC4xMzcwMTksMy42NTc1NCAtNS40NDk4NDIsMTAuMjY5NTEgLTIuNjg4NTQ4LDE1LjA1MjUxIDE0LjY3NTkzOCwyNS40MjEwNyAyOS4zNTE4NzcsNTAuODQyMTQgNDQuMDI3ODE2LDc2LjI2MzIxIDIuNzYxMjkzLDQuNzgzIDguNjczNTU5LDYuMDk4MiAxMy4wNjg2NzMsMi43NTQzNSAyOC41NDgzNDUsLTIxLjcxOTg4IDUyLjUxMDcyNSwtNDguOTU3NjMgNzIuMDEzODc1LC04MS43NjU1MyAyLjgyMjA0LC00Ljc0NzE4IDMuMDA0NTgsLTEyLjY5MDYgMC43Mjg0LC0xNy43MjE4NSAtNy4xMTEwMywtMTUuNzE4MTMgLTIxLjA5MDk4LC01MC4xMzA1MiAtMjUuNjg2MjQsLTg5LjA2MTE2IC0wLjY0NzM1LC01LjQ4NDI3IC01LjQzMDk1LC05Ljk1MzUxIC0xMC45NTM4LC05Ljk1MzUzIGwgLTI0LjQ0MDY3NSwtNmUtNSBjIC01LjUyMjg0NywtMmUtNSAtMTAuNzEzNTk4LDQuNDIzMjEgLTExLjg5MDk4LDkuODE4NTQgeiIgLz48cGF0aAogICAgICAgICAgIGlkPSJwYXRoMy05LTMtMy04LTctMy0xLTctMy02LTktMi02IgogICAgICAgICAgIHN0eWxlPSJmaWxsOiMwMDc1YmY7ZmlsbC1vcGFjaXR5OjE7ZmlsbC1ydWxlOm5vbnplcm87c3Ryb2tlOm5vbmU7c3Ryb2tlLXdpZHRoOjUuODc2Mzc7c3Ryb2tlLWRhc2hhcnJheTpub25lO3N0cm9rZS1vcGFjaXR5OjEiCiAgICAgICAgICAgZD0ibSA3Mi4xODcxNDUsLTYwOC42MzQ1NSBjIC04LjM4OTM2OSwzOC40NDQwNiAtMjcuMjgyMDkzLDcwLjgzNDQyIC01NC4xNzg1MjEsOTQuNjEzNTIgLTQuMTM3MDE5LDMuNjU3NTQgLTUuNDQ5ODQyLDEwLjI2OTUxIC0yLjY4ODU0OCwxNS4wNTI1MSAxNC42NzU5MzgsMjUuNDIxMDcgMjkuMzUxODc3LDUwLjg0MjE0IDQ0LjAyNzgxNiw3Ni4yNjMyMSAyLjc2MTI5Myw0Ljc4MyA4LjY3MzU1OSw2LjA5ODIgMTMuMDY4NjczLDIuNzU0MzUgMjguNTQ4MzQ1LC0yMS43MTk4OCA1Mi41MTA3MjUsLTQ4Ljk1NzYzIDcyLjAxMzg3NSwtODEuNzY1NTMgMi44MjIwNCwtNC43NDcxOCAzLjAwNDU4LC0xMi42OTA2IDAuNzI4NCwtMTcuNzIxODUgLTcuMTExMDMsLTE1LjcxODEzIC0yMS4wOTA5OCwtNTAuMTMwNTIgLTI1LjY4NjI0LC04OS4wNjExNiAtMC42NDczNSwtNS40ODQyNyAtNS40MzA5NSwtOS45NTM1MSAtMTAuOTUzOCwtOS45NTM1MyBsIC0yNC40NDA2NzUsLTZlLTUgYyAtNS41MjI4NDcsLTJlLTUgLTEwLjcxMzU5OCw0LjQyMzIxIC0xMS44OTA5OCw5LjgxODU0IHoiCiAgICAgICAgICAgdHJhbnNmb3JtPSJyb3RhdGUoMTIwLDE1OC40NjQ3LC00OTUuOTgyNzUpIiAvPjxwYXRoCiAgICAgICAgICAgaWQ9InBhdGgzLTktMy0zLTgtNy0zLTUtMi05LTMtMi02LTItMSIKICAgICAgICAgICBzdHlsZT0iZmlsbDojMjkyMzVjO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lO3N0cm9rZS13aWR0aDo1Ljg3NjM3O3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgICAgIGQ9Im0gNzIuMTg3MTQ1LC02MDguNjM0NTUgYyAtOC4zODkzNjksMzguNDQ0MDYgLTI3LjI4MjA5Myw3MC44MzQ0MiAtNTQuMTc4NTIxLDk0LjYxMzUyIC00LjEzNzAxOSwzLjY1NzU0IC01LjQ0OTg0MiwxMC4yNjk1MSAtMi42ODg1NDgsMTUuMDUyNTEgMTQuNjc1OTM4LDI1LjQyMTA3IDI5LjM1MTg3Nyw1MC44NDIxNCA0NC4wMjc4MTYsNzYuMjYzMjEgMi43NjEyOTMsNC43ODMgOC42NzM1NTksNi4wOTgyIDEzLjA2ODY3MywyLjc1NDM1IDI4LjU0ODM0NSwtMjEuNzE5ODggNTIuNTEwNzI1LC00OC45NTc2MyA3Mi4wMTM4NzUsLTgxLjc2NTUzIDIuODIyMDQsLTQuNzQ3MTggMy4wMDQ1OCwtMTIuNjkwNiAwLjcyODQsLTE3LjcyMTg1IC03LjExMTAzLC0xNS43MTgxMyAtMjEuMDkwOTgsLTUwLjEzMDUyIC0yNS42ODYyNCwtODkuMDYxMTYgLTAuNjQ3MzUsLTUuNDg0MjcgLTUuNDMwOTUsLTkuOTUzNTEgLTEwLjk1MzgsLTkuOTUzNTMgbCAtMjQuNDQwNjc1LC02ZS01IGMgLTUuNTIyODQ3LC0yZS01IC0xMC43MTM1OTgsNC40MjMyMSAtMTEuODkwOTgsOS44MTg1NCB6IgogICAgICAgICAgIHRyYW5zZm9ybT0icm90YXRlKC0xMjAsMTU4LjQ1NDE1LC00OTUuOTkxMjIpIiAvPjwvZz48ZwogICAgICAgICBpZD0iZzExLTctMC0wLTktMC0yLTg5LTAiCiAgICAgICAgIHRyYW5zZm9ybT0ibWF0cml4KDAsMC41OTY2NzEyNSwwLjU5NjY3MTI1LDAsNjMwLjEzMjg0LDI1LjY4NDIyMSkiCiAgICAgICAgIHN0eWxlPSJzdHJva2Utd2lkdGg6MC40NDM0MzIiPjxwYXRoCiAgICAgICAgICAgaWQ9InBhdGgzLTktMy0zLTgtNy0wLTEtMC0zLTE2LTctNiIKICAgICAgICAgICBzdHlsZT0iZmlsbDojZmZjYzAwO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lO3N0cm9rZS13aWR0aDo1Ljg3NjM3O3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgICAgIGQ9Im0gNzIuMTg3MTQ1LC02MDguNjM0NTUgYyAtOC4zODkzNjksMzguNDQ0MDYgLTI3LjI4MjA5Myw3MC44MzQ0MiAtNTQuMTc4NTIxLDk0LjYxMzUyIC00LjEzNzAxOSwzLjY1NzU0IC01LjQ0OTg0MiwxMC4yNjk1MSAtMi42ODg1NDgsMTUuMDUyNTEgMTQuNjc1OTM4LDI1LjQyMTA3IDI5LjM1MTg3Nyw1MC44NDIxNCA0NC4wMjc4MTYsNzYuMjYzMjEgMi43NjEyOTMsNC43ODMgOC42NzM1NTksNi4wOTgyIDEzLjA2ODY3MywyLjc1NDM1IDI4LjU0ODM0NSwtMjEuNzE5ODggNTIuNTEwNzI1LC00OC45NTc2MyA3Mi4wMTM4NzUsLTgxLjc2NTUzIDIuODIyMDQsLTQuNzQ3MTggMy4wMDQ1OCwtMTIuNjkwNiAwLjcyODQsLTE3LjcyMTg1IC03LjExMTAzLC0xNS43MTgxMyAtMjEuMDkwOTgsLTUwLjEzMDUyIC0yNS42ODYyNCwtODkuMDYxMTYgLTAuNjQ3MzUsLTUuNDg0MjcgLTUuNDMwOTUsLTkuOTUzNTEgLTEwLjk1MzgsLTkuOTUzNTMgbCAtMjQuNDQwNjc1LC02ZS01IGMgLTUuNTIyODQ3LC0yZS01IC0xMC43MTM1OTgsNC40MjMyMSAtMTEuODkwOTgsOS44MTg1NCB6IiAvPjxwYXRoCiAgICAgICAgICAgaWQ9InBhdGgzLTktMy0zLTgtNy0zLTEtNy0zLTYtMi0zNi0zIgogICAgICAgICAgIHN0eWxlPSJmaWxsOiNmMTg3MDA7ZmlsbC1vcGFjaXR5OjE7ZmlsbC1ydWxlOm5vbnplcm87c3Ryb2tlOm5vbmU7c3Ryb2tlLXdpZHRoOjUuODc2Mzc7c3Ryb2tlLWRhc2hhcnJheTpub25lO3N0cm9rZS1vcGFjaXR5OjEiCiAgICAgICAgICAgZD0ibSA3Mi4xODcxNDUsLTYwOC42MzQ1NSBjIC04LjM4OTM2OSwzOC40NDQwNiAtMjcuMjgyMDkzLDcwLjgzNDQyIC01NC4xNzg1MjEsOTQuNjEzNTIgLTQuMTM3MDE5LDMuNjU3NTQgLTUuNDQ5ODQyLDEwLjI2OTUxIC0yLjY4ODU0OCwxNS4wNTI1MSAxNC42NzU5MzgsMjUuNDIxMDcgMjkuMzUxODc3LDUwLjg0MjE0IDQ0LjAyNzgxNiw3Ni4yNjMyMSAyLjc2MTI5Myw0Ljc4MyA4LjY3MzU1OSw2LjA5ODIgMTMuMDY4NjczLDIuNzU0MzUgMjguNTQ4MzQ1LC0yMS43MTk4OCA1Mi41MTA3MjUsLTQ4Ljk1NzYzIDcyLjAxMzg3NSwtODEuNzY1NTMgMi44MjIwNCwtNC43NDcxOCAzLjAwNDU4LC0xMi42OTA2IDAuNzI4NCwtMTcuNzIxODUgLTcuMTExMDMsLTE1LjcxODEzIC0yMS4wOTA5OCwtNTAuMTMwNTIgLTI1LjY4NjI0LC04OS4wNjExNiAtMC42NDczNSwtNS40ODQyNyAtNS40MzA5NSwtOS45NTM1MSAtMTAuOTUzOCwtOS45NTM1MyBsIC0yNC40NDA2NzUsLTZlLTUgYyAtNS41MjI4NDcsLTJlLTUgLTEwLjcxMzU5OCw0LjQyMzIxIC0xMS44OTA5OCw5LjgxODU0IHoiCiAgICAgICAgICAgdHJhbnNmb3JtPSJyb3RhdGUoMTIwLDE1OC40NjQ3LC00OTUuOTgyNzUpIiAvPjxwYXRoCiAgICAgICAgICAgaWQ9InBhdGgzLTktMy0zLTgtNy0zLTUtMi05LTMtMi0xLTEtMiIKICAgICAgICAgICBzdHlsZT0iZmlsbDojY2UxNjI1O2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lO3N0cm9rZS13aWR0aDo1Ljg3NjM3O3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgICAgIGQ9Im0gNzIuMTg3MTQ1LC02MDguNjM0NTUgYyAtOC4zODkzNjksMzguNDQ0MDYgLTI3LjI4MjA5Myw3MC44MzQ0MiAtNTQuMTc4NTIxLDk0LjYxMzUyIC00LjEzNzAxOSwzLjY1NzU0IC01LjQ0OTg0MiwxMC4yNjk1MSAtMi42ODg1NDgsMTUuMDUyNTEgMTQuNjc1OTM4LDI1LjQyMTA3IDI5LjM1MTg3Nyw1MC44NDIxNCA0NC4wMjc4MTYsNzYuMjYzMjEgMi43NjEyOTMsNC43ODMgOC42NzM1NTksNi4wOTgyIDEzLjA2ODY3MywyLjc1NDM1IDI4LjU0ODM0NSwtMjEuNzE5ODggNTIuNTEwNzI1LC00OC45NTc2MyA3Mi4wMTM4NzUsLTgxLjc2NTUzIDIuODIyMDQsLTQuNzQ3MTggMy4wMDQ1OCwtMTIuNjkwNiAwLjcyODQsLTE3LjcyMTg1IC03LjExMTAzLC0xNS43MTgxMyAtMjEuMDkwOTgsLTUwLjEzMDUyIC0yNS42ODYyNCwtODkuMDYxMTYgLTAuNjQ3MzUsLTUuNDg0MjcgLTUuNDMwOTUsLTkuOTUzNTEgLTEwLjk1MzgsLTkuOTUzNTMgbCAtMjQuNDQwNjc1LC02ZS01IGMgLTUuNTIyODQ3LC0yZS01IC0xMC43MTM1OTgsNC40MjMyMSAtMTEuODkwOTgsOS44MTg1NCB6IgogICAgICAgICAgIHRyYW5zZm9ybT0icm90YXRlKC0xMjAsMTU4LjQ1NDE1LC00OTUuOTkxMjIpIiAvPjwvZz48ZwogICAgICAgICBpZD0iZzExLTctMC0wLTktMC0yLTgtMi0wIgogICAgICAgICB0cmFuc2Zvcm09Im1hdHJpeCgwLDAuNTk2NjcxMjUsMC41OTY2NzEyNSwwLDYzMC40MzU2NSwzMDAuMzEyODQpIgogICAgICAgICBzdHlsZT0ic3Ryb2tlLXdpZHRoOjAuNDQzNDMyIj48cGF0aAogICAgICAgICAgIGlkPSJwYXRoMy05LTMtMy04LTctMC0xLTAtMy0xNi02LTktNiIKICAgICAgICAgICBzdHlsZT0iZmlsbDojZmZjYzAwO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lO3N0cm9rZS13aWR0aDo1Ljg3NjM3O3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgICAgIGQ9Im0gNzIuMTg3MTQ1LC02MDguNjM0NTUgYyAtOC4zODkzNjksMzguNDQ0MDYgLTI3LjI4MjA5Myw3MC44MzQ0MiAtNTQuMTc4NTIxLDk0LjYxMzUyIC00LjEzNzAxOSwzLjY1NzU0IC01LjQ0OTg0MiwxMC4yNjk1MSAtMi42ODg1NDgsMTUuMDUyNTEgMTQuNjc1OTM4LDI1LjQyMTA3IDI5LjM1MTg3Nyw1MC44NDIxNCA0NC4wMjc4MTYsNzYuMjYzMjEgMi43NjEyOTMsNC43ODMgOC42NzM1NTksNi4wOTgyIDEzLjA2ODY3MywyLjc1NDM1IDI4LjU0ODM0NSwtMjEuNzE5ODggNTIuNTEwNzI1LC00OC45NTc2MyA3Mi4wMTM4NzUsLTgxLjc2NTUzIDIuODIyMDQsLTQuNzQ3MTggMy4wMDQ1OCwtMTIuNjkwNiAwLjcyODQsLTE3LjcyMTg1IC03LjExMTAzLC0xNS43MTgxMyAtMjEuMDkwOTgsLTUwLjEzMDUyIC0yNS42ODYyNCwtODkuMDYxMTYgLTAuNjQ3MzUsLTUuNDg0MjcgLTUuNDMwOTUsLTkuOTUzNTEgLTEwLjk1MzgsLTkuOTUzNTMgbCAtMjQuNDQwNjc1LC02ZS01IGMgLTUuNTIyODQ3LC0yZS01IC0xMC43MTM1OTgsNC40MjMyMSAtMTEuODkwOTgsOS44MTg1NCB6IiAvPjxwYXRoCiAgICAgICAgICAgaWQ9InBhdGgzLTktMy0zLTgtNy0zLTEtNy0zLTYtMi0zLTMtMSIKICAgICAgICAgICBzdHlsZT0iZmlsbDojZjE4NzAwO2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lO3N0cm9rZS13aWR0aDo1Ljg3NjM3O3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgICAgIGQ9Im0gNzIuMTg3MTQ1LC02MDguNjM0NTUgYyAtOC4zODkzNjksMzguNDQ0MDYgLTI3LjI4MjA5Myw3MC44MzQ0MiAtNTQuMTc4NTIxLDk0LjYxMzUyIC00LjEzNzAxOSwzLjY1NzU0IC01LjQ0OTg0MiwxMC4yNjk1MSAtMi42ODg1NDgsMTUuMDUyNTEgMTQuNjc1OTM4LDI1LjQyMTA3IDI5LjM1MTg3Nyw1MC44NDIxNCA0NC4wMjc4MTYsNzYuMjYzMjEgMi43NjEyOTMsNC43ODMgOC42NzM1NTksNi4wOTgyIDEzLjA2ODY3MywyLjc1NDM1IDI4LjU0ODM0NSwtMjEuNzE5ODggNTIuNTEwNzI1LC00OC45NTc2MyA3Mi4wMTM4NzUsLTgxLjc2NTUzIDIuODIyMDQsLTQuNzQ3MTggMy4wMDQ1OCwtMTIuNjkwNiAwLjcyODQsLTE3LjcyMTg1IC03LjExMTAzLC0xNS43MTgxMyAtMjEuMDkwOTgsLTUwLjEzMDUyIC0yNS42ODYyNCwtODkuMDYxMTYgLTAuNjQ3MzUsLTUuNDg0MjcgLTUuNDMwOTUsLTkuOTUzNTEgLTEwLjk1MzgsLTkuOTUzNTMgbCAtMjQuNDQwNjc1LC02ZS01IGMgLTUuNTIyODQ3LC0yZS01IC0xMC43MTM1OTgsNC40MjMyMSAtMTEuODkwOTgsOS44MTg1NCB6IgogICAgICAgICAgIHRyYW5zZm9ybT0icm90YXRlKDEyMCwxNTguNDY0NywtNDk1Ljk4Mjc1KSIgLz48cGF0aAogICAgICAgICAgIGlkPSJwYXRoMy05LTMtMy04LTctMy01LTItOS0zLTItMS04LTEtNSIKICAgICAgICAgICBzdHlsZT0iZmlsbDojY2UxNjI1O2ZpbGwtb3BhY2l0eToxO2ZpbGwtcnVsZTpub256ZXJvO3N0cm9rZTpub25lO3N0cm9rZS13aWR0aDo1Ljg3NjM3O3N0cm9rZS1kYXNoYXJyYXk6bm9uZTtzdHJva2Utb3BhY2l0eToxIgogICAgICAgICAgIGQ9Im0gNzIuMTg3MTQ1LC02MDguNjM0NTUgYyAtOC4zODkzNjksMzguNDQ0MDYgLTI3LjI4MjA5Myw3MC44MzQ0MiAtNTQuMTc4NTIxLDk0LjYxMzUyIC00LjEzNzAxOSwzLjY1NzU0IC01LjQ0OTg0MiwxMC4yNjk1MSAtMi42ODg1NDgsMTUuMDUyNTEgMTQuNjc1OTM4LDI1LjQyMTA3IDI5LjM1MTg3Nyw1MC44NDIxNCA0NC4wMjc4MTYsNzYuMjYzMjEgMi43NjEyOTMsNC43ODMgOC42NzM1NTksNi4wOTgyIDEzLjA2ODY3MywyLjc1NDM1IDI4LjU0ODM0NSwtMjEuNzE5ODggNTIuNTEwNzI1LC00OC45NTc2MyA3Mi4wMTM4NzUsLTgxLjc2NTUzIDIuODIyMDQsLTQuNzQ3MTggMy4wMDQ1OCwtMTIuNjkwNiAwLjcyODQsLTE3LjcyMTg1IC03LjExMTAzLC0xNS43MTgxMyAtMjEuMDkwOTgsLTUwLjEzMDUyIC0yNS42ODYyNCwtODkuMDYxMTYgLTAuNjQ3MzUsLTUuNDg0MjcgLTUuNDMwOTUsLTkuOTUzNTEgLTEwLjk1MzgsLTkuOTUzNTMgbCAtMjQuNDQwNjc1LC02ZS01IGMgLTUuNTIyODQ3LC0yZS01IC0xMC43MTM1OTgsNC40MjMyMSAtMTEuODkwOTgsOS44MTg1NCB6IgogICAgICAgICAgIHRyYW5zZm9ybT0icm90YXRlKC0xMjAsMTU4LjQ1NDE0LC00OTUuOTkxMjIpIiAvPjwvZz48ZwogICAgICAgICBpZD0iZzExLTctMC0wLTktMC0wLTAtOTQtNSIKICAgICAgICAgdHJhbnNmb3JtPSJtYXRyaXgoMC41MTY3MzI0NiwtMC4yOTgzMzU2MiwwLjI5ODMzNTYyLDAuNTE2NzMyNDYsNDc4LjgyMDExLDU2MC4yODk3KSIKICAgICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDowLjQ0MzQzMiI+PHBhdGgKICAgICAgICAgICBpZD0icGF0aDMtOS0zLTMtOC03LTAtMS0wLTMtMS0xLTc4LTQiCiAgICAgICAgICAgc3R5bGU9ImZpbGw6IzAwOGI5MjtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6NS44NzYzNztzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgICAgICBkPSJtIDcyLjE4NzE0NSwtNjA4LjYzNDU1IGMgLTguMzg5MzY5LDM4LjQ0NDA2IC0yNy4yODIwOTMsNzAuODM0NDIgLTU0LjE3ODUyMSw5NC42MTM1MiAtNC4xMzcwMTksMy42NTc1NCAtNS40NDk4NDIsMTAuMjY5NTEgLTIuNjg4NTQ4LDE1LjA1MjUxIDE0LjY3NTkzOCwyNS40MjEwNyAyOS4zNTE4NzcsNTAuODQyMTQgNDQuMDI3ODE2LDc2LjI2MzIxIDIuNzYxMjkzLDQuNzgzIDguNjczNTU5LDYuMDk4MiAxMy4wNjg2NzMsMi43NTQzNSAyOC41NDgzNDUsLTIxLjcxOTg4IDUyLjUxMDcyNSwtNDguOTU3NjMgNzIuMDEzODc1LC04MS43NjU1MyAyLjgyMjA0LC00Ljc0NzE4IDMuMDA0NTgsLTEyLjY5MDYgMC43Mjg0LC0xNy43MjE4NSAtNy4xMTEwMywtMTUuNzE4MTMgLTIxLjA5MDk4LC01MC4xMzA1MiAtMjUuNjg2MjQsLTg5LjA2MTE2IC0wLjY0NzM1LC01LjQ4NDI3IC01LjQzMDk1LC05Ljk1MzUxIC0xMC45NTM4LC05Ljk1MzUzIGwgLTI0LjQ0MDY3NSwtNmUtNSBjIC01LjUyMjg0NywtMmUtNSAtMTAuNzEzNTk4LDQuNDIzMjEgLTExLjg5MDk4LDkuODE4NTQgeiIgLz48cGF0aAogICAgICAgICAgIGlkPSJwYXRoMy05LTMtMy04LTctMy0xLTctMy02LTktOS00LTciCiAgICAgICAgICAgc3R5bGU9ImZpbGw6IzAwNzViZjtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6NS44NzYzNztzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgICAgICBkPSJtIDcyLjE4NzE0NSwtNjA4LjYzNDU1IGMgLTguMzg5MzY5LDM4LjQ0NDA2IC0yNy4yODIwOTMsNzAuODM0NDIgLTU0LjE3ODUyMSw5NC42MTM1MiAtNC4xMzcwMTksMy42NTc1NCAtNS40NDk4NDIsMTAuMjY5NTEgLTIuNjg4NTQ4LDE1LjA1MjUxIDE0LjY3NTkzOCwyNS40MjEwNyAyOS4zNTE4NzcsNTAuODQyMTQgNDQuMDI3ODE2LDc2LjI2MzIxIDIuNzYxMjkzLDQuNzgzIDguNjczNTU5LDYuMDk4MiAxMy4wNjg2NzMsMi43NTQzNSAyOC41NDgzNDUsLTIxLjcxOTg4IDUyLjUxMDcyNSwtNDguOTU3NjMgNzIuMDEzODc1LC04MS43NjU1MyAyLjgyMjA0LC00Ljc0NzE4IDMuMDA0NTgsLTEyLjY5MDYgMC43Mjg0LC0xNy43MjE4NSAtNy4xMTEwMywtMTUuNzE4MTMgLTIxLjA5MDk4LC01MC4xMzA1MiAtMjUuNjg2MjQsLTg5LjA2MTE2IC0wLjY0NzM1LC01LjQ4NDI3IC01LjQzMDk1LC05Ljk1MzUxIC0xMC45NTM4LC05Ljk1MzUzIGwgLTI0LjQ0MDY3NSwtNmUtNSBjIC01LjUyMjg0NywtMmUtNSAtMTAuNzEzNTk4LDQuNDIzMjEgLTExLjg5MDk4LDkuODE4NTQgeiIKICAgICAgICAgICB0cmFuc2Zvcm09InJvdGF0ZSgxMjAsMTU4LjQ2NDcsLTQ5NS45ODI3NSkiIC8+PHBhdGgKICAgICAgICAgICBpZD0icGF0aDMtOS0zLTMtOC03LTMtNS0yLTktMy0yLTYtNy01LTYiCiAgICAgICAgICAgc3R5bGU9ImZpbGw6IzI5MjM1YztmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6NS44NzYzNztzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgICAgICBkPSJtIDcyLjE4NzE0NSwtNjA4LjYzNDU1IGMgLTguMzg5MzY5LDM4LjQ0NDA2IC0yNy4yODIwOTMsNzAuODM0NDIgLTU0LjE3ODUyMSw5NC42MTM1MiAtNC4xMzcwMTksMy42NTc1NCAtNS40NDk4NDIsMTAuMjY5NTEgLTIuNjg4NTQ4LDE1LjA1MjUxIDE0LjY3NTkzOCwyNS40MjEwNyAyOS4zNTE4NzcsNTAuODQyMTQgNDQuMDI3ODE2LDc2LjI2MzIxIDIuNzYxMjkzLDQuNzgzIDguNjczNTU5LDYuMDk4MiAxMy4wNjg2NzMsMi43NTQzNSAyOC41NDgzNDUsLTIxLjcxOTg4IDUyLjUxMDcyNSwtNDguOTU3NjMgNzIuMDEzODc1LC04MS43NjU1MyAyLjgyMjA0LC00Ljc0NzE4IDMuMDA0NTgsLTEyLjY5MDYgMC43Mjg0LC0xNy43MjE4NSAtNy4xMTEwMywtMTUuNzE4MTMgLTIxLjA5MDk4LC01MC4xMzA1MiAtMjUuNjg2MjQsLTg5LjA2MTE2IC0wLjY0NzM1LC01LjQ4NDI3IC01LjQzMDk1LC05Ljk1MzUxIC0xMC45NTM4LC05Ljk1MzUzIGwgLTI0LjQ0MDY3NSwtNmUtNSBjIC01LjUyMjg0NywtMmUtNSAtMTAuNzEzNTk4LDQuNDIzMjEgLTExLjg5MDk4LDkuODE4NTQgeiIKICAgICAgICAgICB0cmFuc2Zvcm09InJvdGF0ZSgtMTIwLDE1OC40NTQxNSwtNDk1Ljk5MTIyKSIgLz48L2c+PGcKICAgICAgICAgaWQ9ImcxMS03LTAtMC05LTAtMC0wLTktMC01IgogICAgICAgICB0cmFuc2Zvcm09Im1hdHJpeCgwLjUxNjczMjQ2LC0wLjI5ODMzNTYyLDAuMjk4MzM1NjIsMC41MTY3MzI0NiwyNDEuOTU0NjcsNjk4LjczMjUxKSIKICAgICAgICAgc3R5bGU9InN0cm9rZS13aWR0aDowLjQ0MzQzMiI+PHBhdGgKICAgICAgICAgICBpZD0icGF0aDMtOS0zLTMtOC03LTAtMS0wLTMtMS0xLTUtMy02IgogICAgICAgICAgIHN0eWxlPSJmaWxsOiMwMDhiOTI7ZmlsbC1vcGFjaXR5OjE7ZmlsbC1ydWxlOm5vbnplcm87c3Ryb2tlOm5vbmU7c3Ryb2tlLXdpZHRoOjUuODc2Mzc7c3Ryb2tlLWRhc2hhcnJheTpub25lO3N0cm9rZS1vcGFjaXR5OjEiCiAgICAgICAgICAgZD0ibSA3Mi4xODcxNDUsLTYwOC42MzQ1NSBjIC04LjM4OTM2OSwzOC40NDQwNiAtMjcuMjgyMDkzLDcwLjgzNDQyIC01NC4xNzg1MjEsOTQuNjEzNTIgLTQuMTM3MDE5LDMuNjU3NTQgLTUuNDQ5ODQyLDEwLjI2OTUxIC0yLjY4ODU0OCwxNS4wNTI1MSAxNC42NzU5MzgsMjUuNDIxMDcgMjkuMzUxODc3LDUwLjg0MjE0IDQ0LjAyNzgxNiw3Ni4yNjMyMSAyLjc2MTI5Myw0Ljc4MyA4LjY3MzU1OSw2LjA5ODIgMTMuMDY4NjczLDIuNzU0MzUgMjguNTQ4MzQ1LC0yMS43MTk4OCA1Mi41MTA3MjUsLTQ4Ljk1NzYzIDcyLjAxMzg3NSwtODEuNzY1NTMgMi44MjIwNCwtNC43NDcxOCAzLjAwNDU4LC0xMi42OTA2IDAuNzI4NCwtMTcuNzIxODUgLTcuMTExMDMsLTE1LjcxODEzIC0yMS4wOTA5OCwtNTAuMTMwNTIgLTI1LjY4NjI0LC04OS4wNjExNiAtMC42NDczNSwtNS40ODQyNyAtNS40MzA5NSwtOS45NTM1MSAtMTAuOTUzOCwtOS45NTM1MyBsIC0yNC40NDA2NzUsLTZlLTUgYyAtNS41MjI4NDcsLTJlLTUgLTEwLjcxMzU5OCw0LjQyMzIxIC0xMS44OTA5OCw5LjgxODU0IHoiIC8+PHBhdGgKICAgICAgICAgICBpZD0icGF0aDMtOS0zLTMtOC03LTMtMS03LTMtNi05LTktMS02LTkiCiAgICAgICAgICAgc3R5bGU9ImZpbGw6IzAwNzViZjtmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6NS44NzYzNztzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgICAgICBkPSJtIDcyLjE4NzE0NSwtNjA4LjYzNDU1IGMgLTguMzg5MzY5LDM4LjQ0NDA2IC0yNy4yODIwOTMsNzAuODM0NDIgLTU0LjE3ODUyMSw5NC42MTM1MiAtNC4xMzcwMTksMy42NTc1NCAtNS40NDk4NDIsMTAuMjY5NTEgLTIuNjg4NTQ4LDE1LjA1MjUxIDE0LjY3NTkzOCwyNS40MjEwNyAyOS4zNTE4NzcsNTAuODQyMTQgNDQuMDI3ODE2LDc2LjI2MzIxIDIuNzYxMjkzLDQuNzgzIDguNjczNTU5LDYuMDk4MiAxMy4wNjg2NzMsMi43NTQzNSAyOC41NDgzNDUsLTIxLjcxOTg4IDUyLjUxMDcyNSwtNDguOTU3NjMgNzIuMDEzODc1LC04MS43NjU1MyAyLjgyMjA0LC00Ljc0NzE4IDMuMDA0NTgsLTEyLjY5MDYgMC43Mjg0LC0xNy43MjE4NSAtNy4xMTEwMywtMTUuNzE4MTMgLTIxLjA5MDk4LC01MC4xMzA1MiAtMjUuNjg2MjQsLTg5LjA2MTE2IC0wLjY0NzM1LC01LjQ4NDI3IC01LjQzMDk1LC05Ljk1MzUxIC0xMC45NTM4LC05Ljk1MzUzIGwgLTI0LjQ0MDY3NSwtNmUtNSBjIC01LjUyMjg0NywtMmUtNSAtMTAuNzEzNTk4LDQuNDIzMjEgLTExLjg5MDk4LDkuODE4NTQgeiIKICAgICAgICAgICB0cmFuc2Zvcm09InJvdGF0ZSgxMjAsMTU4LjQ2NDcsLTQ5NS45ODI3NSkiIC8+PHBhdGgKICAgICAgICAgICBpZD0icGF0aDMtOS0zLTMtOC03LTMtNS0yLTktMy0yLTYtNy0yLTEwLTMiCiAgICAgICAgICAgc3R5bGU9ImZpbGw6IzI5MjM1YztmaWxsLW9wYWNpdHk6MTtmaWxsLXJ1bGU6bm9uemVybztzdHJva2U6bm9uZTtzdHJva2Utd2lkdGg6NS44NzYzNztzdHJva2UtZGFzaGFycmF5Om5vbmU7c3Ryb2tlLW9wYWNpdHk6MSIKICAgICAgICAgICBkPSJtIDcyLjE4NzE0NSwtNjA4LjYzNDU1IGMgLTguMzg5MzY5LDM4LjQ0NDA2IC0yNy4yODIwOTMsNzAuODM0NDIgLTU0LjE3ODUyMSw5NC42MTM1MiAtNC4xMzcwMTksMy42NTc1NCAtNS40NDk4NDIsMTAuMjY5NTEgLTIuNjg4NTQ4LDE1LjA1MjUxIDE0LjY3NTkzOCwyNS40MjEwNyAyOS4zNTE4NzcsNTAuODQyMTQgNDQuMDI3ODE2LDc2LjI2MzIxIDIuNzYxMjkzLDQuNzgzIDguNjczNTU5LDYuMDk4MiAxMy4wNjg2NzMsMi43NTQzNSAyOC41NDgzNDUsLTIxLjcxOTg4IDUyLjUxMDcyNSwtNDguOTU3NjMgNzIuMDEzODc1LC04MS43NjU1MyAyLjgyMjA0LC00Ljc0NzE4IDMuMDA0NTgsLTEyLjY5MDYgMC43Mjg0LC0xNy43MjE4NSAtNy4xMTEwMywtMTUuNzE4MTMgLTIxLjA5MDk4LC01MC4xMzA1MiAtMjUuNjg2MjQsLTg5LjA2MTE2IC0wLjY0NzM1LC01LjQ4NDI3IC01LjQzMDk1LC05Ljk1MzUxIC0xMC45NTM4LC05Ljk1MzUzIGwgLTI0LjQ0MDY3NSwtNmUtNSBjIC01LjUyMjg0NywtMmUtNSAtMTAuNzEzNTk4LDQuNDIzMjEgLTExLjg5MDk4LDkuODE4NTQgeiIKICAgICAgICAgICB0cmFuc2Zvcm09InJvdGF0ZSgtMTIwLDE1OC40NTQxNSwtNDk1Ljk5MTIyKSIgLz48L2c+PC9nPjwvZz48ZwogICAgIGlkPSJsYXllcjEiIC8+PC9zdmc+Cg=="
                        alt="STUPA MAKERS"
                        width={120} // Equivalent to w-40 in a typical Tailwind config (160px)
                        height={40} // Adjust height as needed, maintaining aspect ratio
                        priority
                    />
                </div>
                <nav className="flex gap-2 bg-gray-900 p-1 rounded-lg">
                    <NavButton
                        active={currentView === "viz"}
                        onClick={() => setCurrentView("viz")}
                    >
                        Live
                    </NavButton>
                    <NavButton
                        active={currentView === "animations"}
                        onClick={() => setCurrentView("animations")}
                    >
                        Effekt
                    </NavButton>
                    <NavButton
                        active={currentView === "layout"}
                        onClick={() => setCurrentView("layout")}
                    >
                        Strips
                    </NavButton>
                </nav>
            </header>
            {/* Main Content */}
            <main className="flex-1 flex flex-col md:flex-row overflow-hidden">
                {/* Visualization View */}
                <div
                    className={`h-full flex-col ${currentView === "viz" ? "flex w-full md:w-full" : "hidden md:flex md:w-1/2"}`}
                >
                    <Visualization config={config} />
                </div>

                {/* Right Panel for other tabs */}
                <div
                    className={`flex-1 overflow-y-auto ${currentView === "viz" ? "hidden md:hidden" : "block w-full md:block md:w-1/2"}`}
                >
                    {/* Animations View */}
                    <div
                        className={`h-full overflow-y-auto p-4 md:p-8 ${currentView === "animations" ? "block" : "hidden"}`}
                    >
                        <div className="max-w-6xl mx-auto">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-2xl font-bold text-gray-100">
                                    Animation Configuration
                                </h2>
                                <button
                                    onClick={saveConfig}
                                    disabled={saving}
                                    className="bg-teal-600 hover:bg-teal-500 text-white font-bold py-2 px-6 rounded shadow transition-colors flex items-center gap-2 disabled:opacity-50"
                                >
                                    {saving
                                        ? "Saving..."
                                        : "Save Configuration"}
                                </button>
                            </div>

                            <div className="grid grid-cols-1 gap-8">
                                {/* Idle Animation */}
                                <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
                                    <h3 className="text-xl font-semibold mb-6 text-teal-300 flex items-center gap-2">
                                        <span className="w-2 h-2 rounded-full bg-teal-300"></span>
                                        Idle Animation
                                    </h3>
                                    <AnimationEditor
                                        config={config.animations?.idle}
                                        onChange={updateIdleConfig}
                                        allAnimations={animations}
                                        availableAnimations={animations.filter(
                                            (a) => a.module === "idle",
                                        )}
                                        isRoot={true}
                                    />
                                </div>

                                {/* Object Animation */}
                                <div className="bg-gray-800 rounded-lg p-6 shadow-lg">
                                    <h3 className="text-xl font-semibold mb-6 text-pink-300 flex items-center gap-2">
                                        <span className="w-2 h-2 rounded-full bg-pink-300"></span>
                                        Object Animation
                                    </h3>
                                    <AnimationEditor
                                        config={config.animations?.object}
                                        onChange={updateObjectConfig}
                                        allAnimations={animations}
                                        availableAnimations={animations.filter(
                                            (a) => a.module === "object",
                                        )}
                                        isRoot={true}
                                    />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* New Strips & Layout View */}
                    <div
                        className={`h-full overflow-y-auto p-4 md:p-8 ${currentView === "layout" ? "block" : "hidden"}`}
                    >
                        <div className="max-w-6xl mx-auto">
                            <div className="flex justify-between items-center mb-6">
                                <h2 className="text-2xl font-bold text-gray-100">
                                    Strip Configuration
                                </h2>
                                <button
                                    onClick={saveConfig}
                                    disabled={saving}
                                    className="bg-teal-600 hover:bg-teal-500 text-white font-bold py-2 px-6 rounded shadow transition-colors flex items-center gap-2 disabled:opacity-50"
                                >
                                    {saving
                                        ? "Saving..."
                                        : "Save Configuration"}
                                </button>
                            </div>
                            <LayoutEditor
                                config={{
                                    strips: config.strips,
                                    floor: {
                                        width:
                                            config.projection?.floor?.[2] || 0,
                                        height:
                                            config.projection?.floor?.[3] || 0,
                                    },
                                }}
                                onChange={updateLayoutConfig}
                            />
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

function NavButton({ active, onClick, children }) {
    return (
        <button
            onClick={onClick}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                active
                    ? "bg-gray-700 text-white shadow-sm"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-800"
            }`}
        >
            {children}
        </button>
    );
}
