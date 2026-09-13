import { useEffect, useState } from "react";

// Resolve Geist scale colors from computed CSS so charts match the active theme.
function read(name: string): string {
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || "#888";
}

export interface ChartColors {
  accent: string;
  grid: string;
  axis: string;
  text: string;
  categorical: string[];
  slots: Record<string, string>;
}

function resolve(): ChartColors {
  return {
    accent: read("--ds-blue-700"),
    grid: read("--ds-gray-400"),
    axis: read("--ds-gray-700"),
    text: read("--ds-gray-900"),
    categorical: [
      read("--ds-blue-700"),
      read("--ds-amber-700"),
      read("--ds-green-700"),
      read("--ds-purple-700"),
      read("--ds-teal-700"),
      read("--ds-pink-700"),
      read("--ds-red-700"),
    ],
    slots: {
      breakfast: read("--ds-amber-700"),
      lunch: read("--ds-blue-700"),
      dinner: read("--ds-purple-700"),
    },
  };
}

// Recompute whenever the theme changes (data-theme attr or system preference).
export function useChartColors(): ChartColors {
  const [colors, setColors] = useState<ChartColors>(resolve);
  useEffect(() => {
    const update = () => setColors(resolve());
    const mo = new MutationObserver(update);
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    mq.addEventListener("change", update);
    return () => {
      mo.disconnect();
      mq.removeEventListener("change", update);
    };
  }, []);
  return colors;
}
