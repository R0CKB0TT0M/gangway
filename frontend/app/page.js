"use client";

import { useEffect, useState } from "react";
import Visualization from "../components/Visualization";
import AnimationEditor from "../components/AnimationEditor";

export default function Home() {
    const [currentView, setCurrentView] = useState("viz");
    const [config, setConfig] = useState(null);
    const [rawConfigString, setRawConfigString] = useState("");
    const [animations, setAnimations] = useState([]);
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

    const saveConfig = async () => {
        setSaving(true);
        try {
            // If we are in 'config' view, we might have edited the string directly
            const payload =
                currentView === "config" ? JSON.parse(rawConfigString) : config;

            const res = await fetch("/api/config/", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!res.ok) throw new Error("Failed to save");

            // Reload config to confirm
            const newConfig = await (await fetch("/api/config/")).json();
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
        const res = await fetch("/api/config/");
        const data = await res.json();
        setConfig(data);
        setRawConfigString(JSON.stringify(data, null, 2));
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
                <h1 className="text-xl font-bold text-teal-400 tracking-wider">
                    GANGWAY
                </h1>
                <nav className="flex gap-2 bg-gray-900 p-1 rounded-lg">
                    <NavButton
                        active={currentView === "viz"}
                        onClick={() => setCurrentView("viz")}
                    >
                        Visualization
                    </NavButton>
                    <NavButton
                        active={currentView === "animations"}
                        onClick={() => setCurrentView("animations")}
                    >
                        Animations
                    </NavButton>
                    <NavButton
                        active={currentView === "config"}
                        onClick={() => setCurrentView("config")}
                    >
                        Raw Config
                    </NavButton>
                </nav>
            </header>

            {/* Main Content */}
            <main className="flex-1 overflow-hidden relative">
                {/* Visualization View */}
                <div
                    className={`h-full flex flex-col ${currentView === "viz" ? "block" : "hidden"}`}
                >
                    <Visualization config={config} />
                </div>

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
                                {saving ? "Saving..." : "Save Configuration"}
                            </button>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                            {/* Idle Animation */}
                            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 shadow-lg">
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
                            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 shadow-lg">
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

                {/* Raw Config View */}
                <div
                    className={`h-full flex flex-col p-4 md:p-8 ${currentView === "config" ? "block" : "hidden"}`}
                >
                    <div className="max-w-6xl mx-auto w-full h-full flex flex-col">
                        <div className="flex justify-between items-center mb-6 shrink-0">
                            <h2 className="text-2xl font-bold">
                                Raw Configuration
                            </h2>
                            <div className="flex gap-4">
                                <button
                                    onClick={resetConfig}
                                    className="text-gray-400 hover:text-white transition-colors"
                                >
                                    Reset
                                </button>
                                <button
                                    onClick={saveConfig}
                                    disabled={saving}
                                    className="bg-teal-600 hover:bg-teal-500 text-white font-bold py-2 px-6 rounded shadow transition-colors disabled:opacity-50"
                                >
                                    {saving ? "Saving..." : "Save Raw Config"}
                                </button>
                            </div>
                        </div>
                        <div className="bg-gray-800 rounded-lg p-1 border border-gray-700 flex-1 overflow-hidden">
                            <textarea
                                value={rawConfigString}
                                onChange={(e) =>
                                    setRawConfigString(e.target.value)
                                }
                                className="w-full h-full bg-gray-900 text-green-400 font-mono text-sm p-4 rounded border-none focus:ring-0 focus:outline-none resize-none"
                                spellCheck="false"
                            ></textarea>
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
