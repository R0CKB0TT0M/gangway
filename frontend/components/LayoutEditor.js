"use client";

import { useState, useEffect } from "react";

export default function LayoutEditor({ config, onChange }) {
    // Map API config format to internal state format
    const mapApiStripsToInternal = (apiStrips) => {
        return (apiStrips || []).map((strip) => ({
            id: strip.index, // Using index from API as ID for consistency
            length: strip.len,
            startIndex: strip.index,
            start: strip.start,
            end: strip.end,
        }));
    };

    // Map internal state format back to API config format
    const mapInternalStripsToApi = (internalStrips) => {
        return (internalStrips || []).map((strip) => ({
            index: parseInt(strip.startIndex, 10),
            len: parseInt(strip.length, 10),
            start: strip.start,
            end: strip.end,
        }));
    };

    const [layoutConfig, setLayoutConfig] = useState(() => {
        const initialStrips = mapApiStripsToInternal(config?.strips);
        // We no longer manage floor configuration in this editor, so we only return strips.
        return { strips: initialStrips };
    });

    useEffect(() => {
        const newStrips = mapApiStripsToInternal(config?.strips);
        // Similarly, only update strips from the config prop.
        setLayoutConfig({ strips: newStrips });
    }, [config]);

    const emitChange = (newLayoutState) => {
        const apiStrips = mapInternalStripsToApi(newLayoutState.strips);
        // Only emit changes for strips, as floor is not managed here.
        onChange({ strips: apiStrips });
    };

    const handleStripChange = (index, field, value) => {
        const newStrips = [...layoutConfig.strips];
        const updatedStrip = { ...newStrips[index] };

        if (field === "length") {
            updatedStrip.length = parseInt(value, 10);
        } else if (field === "startIndex") {
            updatedStrip.startIndex = parseInt(value, 10);
        } else if (
            field === "startX" ||
            field === "startY" ||
            field === "endX" ||
            field === "endY"
        ) {
            const pointField = field.startsWith("start") ? "start" : "end";
            const coord = field.endsWith("X") ? 0 : 1;
            updatedStrip[pointField] = [...updatedStrip[pointField]];
            updatedStrip[pointField][coord] = parseFloat(value);
        }

        newStrips[index] = updatedStrip;
        const newLayoutConfig = { ...layoutConfig, strips: newStrips };
        setLayoutConfig(newLayoutConfig);
        emitChange(newLayoutConfig);
    };

    const addStrip = () => {
        const newStrips = [
            ...(layoutConfig.strips || []),
            {
                id: Date.now(), // Unique ID for key prop
                length: 1,
                startIndex: 0,
                start: [0.0, 0.0],
                end: [0.0, 0.0],
            },
        ];
        const newLayoutConfig = { ...layoutConfig, strips: newStrips };
        setLayoutConfig(newLayoutConfig);
        emitChange(newLayoutConfig);
    };

    const removeStrip = (index) => {
        const newStrips = (layoutConfig.strips || []).filter(
            (_, i) => i !== index,
        );
        const newLayoutConfig = { ...layoutConfig, strips: newStrips };
        setLayoutConfig(newLayoutConfig);
        emitChange(newLayoutConfig);
    };

    if (!layoutConfig) {
        return (
            <div className="text-gray-400">Loading layout configuration...</div>
        );
    }

    return (
        <div className="space-y-4">
            {/* Strips Configuration List */}
            <div className="space-y-4">
                {(layoutConfig.strips || []).map((strip, index) => (
                    <div
                        key={strip.id || index}
                        className="bg-gray-700 p-4 rounded-md flex flex-col sm:flex-row items-start sm:items-center gap-4 border border-gray-600"
                    >
                        <span className="font-medium text-gray-300 w-full sm:w-auto">
                            Strip {index + 1}:
                        </span>
                        <div className="flex-grow grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label
                                    htmlFor={`strip-startIndex-${index}`}
                                    className="block text-gray-400 text-xs uppercase font-bold mb-1"
                                >
                                    Start Index
                                </label>
                                <input
                                    type="number"
                                    id={`strip-startIndex-${index}`}
                                    value={strip.startIndex}
                                    onChange={(e) =>
                                        handleStripChange(
                                            index,
                                            "startIndex",
                                            e.target.value,
                                        )
                                    }
                                    step="1"
                                    className="w-full bg-gray-600 text-white rounded px-3 py-2 border border-gray-500 focus:border-teal-500 outline-none text-sm"
                                />
                            </div>
                            <div>
                                <label
                                    htmlFor={`strip-length-${index}`}
                                    className="block text-gray-400 text-xs uppercase font-bold mb-1"
                                >
                                    Length
                                </label>
                                <input
                                    type="number"
                                    id={`strip-length-${index}`}
                                    value={strip.length}
                                    onChange={(e) =>
                                        handleStripChange(
                                            index,
                                            "length",
                                            e.target.value,
                                        )
                                    }
                                    step="1"
                                    className="w-full bg-gray-600 text-white rounded px-3 py-2 border border-gray-500 focus:border-teal-500 outline-none text-sm"
                                />
                            </div>
                            <div className="md:col-span-2 grid grid-cols-2 gap-4">
                                <div>
                                    <label
                                        htmlFor={`strip-startX-${index}`}
                                        className="block text-gray-400 text-xs uppercase font-bold mb-1"
                                    >
                                        Start X
                                    </label>
                                    <input
                                        type="number"
                                        id={`strip-startX-${index}`}
                                        value={strip.start?.[0] || 0.0}
                                        onChange={(e) =>
                                            handleStripChange(
                                                index,
                                                "startX",
                                                e.target.value,
                                            )
                                        }
                                        step="0.1"
                                        className="w-full bg-gray-600 text-white rounded px-3 py-2 border border-gray-500 focus:border-teal-500 outline-none text-sm"
                                    />
                                </div>
                                <div>
                                    <label
                                        htmlFor={`strip-startY-${index}`}
                                        className="block text-gray-400 text-xs uppercase font-bold mb-1"
                                    >
                                        Start Y
                                    </label>
                                    <input
                                        type="number"
                                        id={`strip-startY-${index}`}
                                        value={strip.start?.[1] || 0.0}
                                        onChange={(e) =>
                                            handleStripChange(
                                                index,
                                                "startY",
                                                e.target.value,
                                            )
                                        }
                                        step="0.1"
                                        className="w-full bg-gray-600 text-white rounded px-3 py-2 border border-gray-500 focus:border-teal-500 outline-none text-sm"
                                    />
                                </div>
                                <div>
                                    <label
                                        htmlFor={`strip-endX-${index}`}
                                        className="block text-gray-400 text-xs uppercase font-bold mb-1"
                                    >
                                        End X
                                    </label>
                                    <input
                                        type="number"
                                        id={`strip-endX-${index}`}
                                        value={strip.end?.[0] || 0.0}
                                        onChange={(e) =>
                                            handleStripChange(
                                                index,
                                                "endX",
                                                e.target.value,
                                            )
                                        }
                                        step="0.1"
                                        className="w-full bg-gray-600 text-white rounded px-3 py-2 border border-gray-500 focus:border-teal-500 outline-none text-sm"
                                    />
                                </div>
                                <div>
                                    <label
                                        htmlFor={`strip-endY-${index}`}
                                        className="block text-gray-400 text-xs uppercase font-bold mb-1"
                                    >
                                        End Y
                                    </label>
                                    <input
                                        type="number"
                                        id={`strip-endY-${index}`}
                                        value={strip.end?.[1] || 0.0}
                                        onChange={(e) =>
                                            handleStripChange(
                                                index,
                                                "endY",
                                                e.target.value,
                                            )
                                        }
                                        step="0.1"
                                        className="w-full bg-gray-600 text-white rounded px-3 py-2 border border-gray-500 focus:border-teal-500 outline-none text-sm"
                                    />
                                </div>
                            </div>
                        </div>
                        <button
                            onClick={() => removeStrip(index)}
                            className="bg-red-600 hover:bg-red-500 text-white font-bold py-2 px-4 rounded shadow transition-colors shrink-0"
                        >
                            Remove
                        </button>
                    </div>
                ))}
            </div>

            <button
                onClick={addStrip}
                className="bg-teal-600 hover:bg-teal-500 text-white font-bold py-2 px-4 rounded shadow transition-colors"
            >
                Add Strip
            </button>
        </div>
    );
}
