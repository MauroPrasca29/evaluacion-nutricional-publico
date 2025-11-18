import type { ThemeColors } from "@/types"

export const getThemeColors = (view: string): ThemeColors => {
  switch (view) {
    case "dashboard":
      return {
        gradient: "from-amber-50 to-white",
        headerBg: "bg-amber-500",
        headerBorder: "border-amber-600",
        buttonColor: "from-amber-500 to-amber-600",
        accentColor: "text-amber-500",
        cardBorder: "border-amber-200",
        cardBg: "from-white to-amber-50",
      }
    case "children":
      return {
        gradient: "from-blue-50 to-white",
        headerBg: "bg-blue-500",
        headerBorder: "border-blue-600",
        buttonColor: "from-blue-500 to-blue-600",
        accentColor: "text-blue-500",
        cardBorder: "border-blue-200",
        cardBg: "from-white to-blue-50",
      }
    case "reports":
      return {
        gradient: "from-green-50 to-white",
        headerBg: "bg-green-500",
        headerBorder: "border-green-600",
        buttonColor: "from-green-500 to-green-600",
        accentColor: "text-green-500",
        cardBorder: "border-green-200",
        cardBg: "from-white to-green-50",
      }
    case "new-followup":
      return {
        gradient: "from-purple-50 to-white",
        headerBg: "bg-purple-500",
        headerBorder: "border-purple-600",
        buttonColor: "from-purple-500 to-purple-600",
        accentColor: "text-purple-500",
        cardBorder: "border-purple-200",
        cardBg: "from-white to-purple-50",
      }
    case "import-data":
      return {
        gradient: "from-indigo-50 to-white",
        headerBg: "bg-indigo-500",
        headerBorder: "border-indigo-600",
        buttonColor: "from-indigo-500 to-indigo-600",
        accentColor: "text-indigo-500",
        cardBorder: "border-indigo-200",
        cardBg: "from-white to-indigo-50",
      }
    default:
      return {
        gradient: "from-slate-50 to-white",
        headerBg: "bg-slate-500",
        headerBorder: "border-slate-600",
        buttonColor: "from-slate-500 to-slate-600",
        accentColor: "text-slate-500",
        cardBorder: "border-slate-200",
        cardBg: "from-white to-slate-50",
      }
  }
}
