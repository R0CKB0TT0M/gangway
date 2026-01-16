"use client";

import { useEffect, useRef, useState } from "react";

export default function Visualization({ config }) {
    const canvasRef = useRef(null);
    const [showImage, setShowImage] = useState(true);
    const [showObjects, setShowObjects] = useState(true);
    const [showColors, setShowColors] = useState(true);
    const [imageSrc, setImageSrc] = useState("");
    const [scale, setScale] = useState(1);
    const [stats, setStats] = useState(null);
    const containerRef = useRef(null);

    const floorWidth = config?.projection?.floor?.[2] || 800;
    const floorHeight = config?.projection?.floor?.[3] || 600;

    // Handle Resize
    useEffect(() => {
        if (!containerRef.current || !floorWidth || !floorHeight) return;

        const updateScale = () => {
            const container = containerRef.current;
            const containerWidth = container.clientWidth;
            const containerHeight = container.clientHeight;
            const margin = 40; // 20px on each side

            const availableWidth = containerWidth - margin;
            const availableHeight = containerHeight - margin;

            const scaleX = availableWidth / floorWidth;
            const scaleY = availableHeight / floorHeight;

            setScale(Math.min(scaleX, scaleY));
        };

        const observer = new ResizeObserver(updateScale);
        observer.observe(containerRef.current);
        updateScale(); // Initial calculation

        return () => observer.disconnect();
    }, [floorWidth, floorHeight]);

    // Image Refresh Loop with Double Buffering
    useEffect(() => {
        if (!showImage) return;

        let isMounted = true;
        let timeoutId;

        const loadNextImage = () => {
            const nextSrc = `/api/visualization/live_mapped?t=${Date.now()}`;
            const img = new Image();

            img.onload = () => {
                if (isMounted) {
                    setImageSrc(nextSrc);
                    timeoutId = setTimeout(loadNextImage, 200);
                }
            };

            img.onerror = () => {
                if (isMounted) {
                    // On error, keep existing image and try again
                    timeoutId = setTimeout(loadNextImage, 200);
                }
            };

            img.src = nextSrc;
        };

        loadNextImage();

        return () => {
            isMounted = false;
            clearTimeout(timeoutId);
        };
    }, [showImage]);

    // Canvas Render Loop
    useEffect(() => {
        if (!config) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");
        let animationFrameId;
        let isRunning = true;

        const render = async () => {
            // Fetch Data
            try {
                const [ledsRes, objectsRes, fpsRes] = await Promise.all([
                    fetch("/api/data/leds"),
                    fetch("/api/data/objects"),
                    fetch("/api/data/fps"),
                ]);

                if (!isRunning) return;

                const leds = showColors ? await ledsRes.json() : {};
                const objects = showObjects ? await objectsRes.json() : [];
                const fpsData = await fpsRes.json();

                setStats(fpsData);

                // Clear
                ctx.clearRect(0, 0, canvas.width, canvas.height);

                // Draw Strips
                ctx.lineWidth = 4;
                config.strips.forEach((strip) => {
                    ctx.strokeStyle = "#333";
                    ctx.beginPath();
                    ctx.moveTo(strip.start[0], strip.start[1]);
                    ctx.lineTo(strip.end[0], strip.end[1]);
                    ctx.stroke();

                    // Calculate LED positions
                    const dx =
                        (strip.end[0] - strip.start[0]) / (strip.len - 1);
                    const dy =
                        (strip.end[1] - strip.start[1]) / (strip.len - 1);

                    for (let i = 0; i < strip.len; i++) {
                        const x = strip.start[0] + dx * i;
                        const y = strip.start[1] + dy * i;
                        const ledIndex = strip.index + i;

                        // Draw LED
                        const color = leds[ledIndex];
                        if (color) {
                            // Simple RGB approximation from RGBCCT
                            // CCT is ignored for visualization simplicity, or added as white overlay
                            const r = Math.min(
                                255,
                                color.r + color.cw + color.ww,
                            );
                            const g = Math.min(
                                255,
                                color.g + color.cw + color.ww,
                            );
                            const b = Math.min(
                                255,
                                color.b + color.cw + color.ww,
                            );
                            ctx.fillStyle = `rgb(${r},${g},${b})`;
                        } else {
                            ctx.fillStyle = "#111";
                        }

                        ctx.beginPath();
                        ctx.arc(x, y, 3, 0, Math.PI * 2);
                        ctx.fill();
                    }
                });

                // Draw Objects
                ctx.fillStyle = "rgba(255, 0, 0, 0.7)";
                objects.forEach((obj) => {
                    ctx.beginPath();
                    ctx.arc(obj.x, obj.y, 10, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.strokeStyle = "white";
                    ctx.lineWidth = 2;
                    ctx.stroke();
                });
            } catch (e) {
                if (isRunning) console.error("Viz Error:", e);
            }

            if (isRunning) {
                animationFrameId = requestAnimationFrame(render);
            }
        };

        render();

        return () => {
            isRunning = false;
            cancelAnimationFrame(animationFrameId);
        };
    }, [config, showColors, showObjects]);

    return (
        <div className="h-full flex flex-col">
            <div
                ref={containerRef}
                className="flex-1 relative bg-black overflow-hidden flex items-center justify-center"
            >
                {stats && (
                    <div className="absolute top-4 left-4 z-20 bg-black/50 text-teal-400 p-2 rounded text-xs font-mono">
                        <div>FPS: {stats.fps}</div>
                        <div>UPS: {stats.ups}</div>
                        <div className="text-gray-400 mt-1">TPF (ms)</div>
                        <div>Min: {stats.tpf_min}</div>
                        <div>Avg: {stats.tpf_avg}</div>
                        <div>Max: {stats.tpf_max}</div>
                    </div>
                )}
                <div
                    className="relative border border-gray-800 bg-gray-900 shadow-2xl origin-center"
                    style={{
                        width: floorWidth,
                        height: floorHeight,
                        transform: `scale(${scale})`,
                    }}
                >
                    {showImage && imageSrc && (
                        <img
                            src={imageSrc}
                            className="absolute top-0 left-0 w-full h-full object-cover opacity-60"
                            alt="Live View"
                        />
                    )}
                    <canvas
                        ref={canvasRef}
                        width={floorWidth}
                        height={floorHeight}
                        className="absolute top-0 left-0 w-full h-full z-10"
                    />
                </div>
            </div>

            <div className="bg-gray-800 p-4 border-t border-gray-700 flex justify-center gap-8">
                <Label
                    checked={showImage}
                    onChange={setShowImage}
                    label="Show Live Image"
                />
                <Label
                    checked={showObjects}
                    onChange={setShowObjects}
                    label="Show Objects"
                />
                <Label
                    checked={showColors}
                    onChange={setShowColors}
                    label="Show LED Colors"
                />
            </div>
        </div>
    );
}

function Label({ checked, onChange, label }) {
    return (
        <label className="flex items-center space-x-2 cursor-pointer select-none group">
            <div
                className={`w-5 h-5 rounded border border-gray-600 flex items-center justify-center transition-colors ${checked ? "bg-teal-600 border-teal-600" : "bg-gray-700 group-hover:border-gray-500"}`}
            >
                {checked && (
                    <svg
                        className="w-3 h-3 text-white fill-current"
                        viewBox="0 0 20 20"
                    >
                        <path d="M0 11l2-2 5 5L18 3l2 2L7 18z" />
                    </svg>
                )}
            </div>
            <input
                type="checkbox"
                checked={checked}
                onChange={(e) => onChange(e.target.checked)}
                className="hidden"
            />
            <span className="text-gray-300 group-hover:text-white transition-colors">
                {label}
            </span>
        </label>
    );
}
