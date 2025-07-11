import type { ThemeColors } from "@/types"

export const getThemeColors = (view: string): ThemeColors => {
  switch (view) {
    case "children":
      return {
        gradient: "from-blue-50 via-slate-50 to-blue-100",
        headerBg: "bg-blue-50/80",
        headerBorder: "border-blue-200",
        cardBorder: "border-blue-200",
        cardBg: "from-white to-blue-50",
        buttonColor: "from-blue-400 to-blue-500 hover:from-blue-500 hover:to-blue-600",
        accentColor: "text-blue-500",
      }
    case "reports":
      return {
        gradient: "from-green-50 via-slate-50 to-green-100",
        headerBg: "bg-green-50/80",
        headerBorder: "border-green-200",
        cardBorder: "border-green-200",
        cardBg: "from-white to-green-50",
        buttonColor: "from-green-400 to-green-500 hover:from-green-500 hover:to-green-600",
        accentColor: "text-green-500",
      }
    case "new-followup":
      return {
        gradient: "from-purple-50 via-slate-50 to-purple-100",
        headerBg: "bg-purple-50/80",
        headerBorder: "border-purple-200",
        cardBorder: "border-purple-200",
        cardBg: "from-white to-purple-50",
        buttonColor: "from-purple-400 to-purple-500 hover:from-purple-500 hover:to-purple-600",
        accentColor: "text-purple-500",
      }
    case "import-data":
      return {
        gradient: "from-indigo-50 via-slate-50 to-indigo-100",
        headerBg: "bg-indigo-50/80",
        headerBorder: "border-indigo-200",
        cardBorder: "border-indigo-200",
        cardBg: "from-white to-indigo-50",
        buttonColor: "from-indigo-400 to-indigo-500 hover:from-indigo-500 hover:to-indigo-600",
        accentColor: "text-indigo-500",
      }
    case "generate-reports":
      return {
        gradient: "from-pink-50 via-slate-50 to-pink-100",
        headerBg: "bg-pink-50/80",
        headerBorder: "border-pink-200",
        cardBorder: "border-pink-200",
        cardBg: "from-white to-pink-50",
        buttonColor: "from-pink-400 to-pink-500 hover:from-pink-500 hover:to-pink-600",
        accentColor: "text-pink-500",
      }
    default: // dashboard
      return {
        gradient: "from-amber-50 via-slate-50 to-amber-100",
        headerBg: "bg-amber-50/80",
        headerBorder: "border-amber-200",
        cardBorder: "border-amber-200",
        cardBg: "from-white to-amber-50",
        buttonColor: "from-amber-400 to-amber-500 hover:from-amber-500 hover:to-amber-600",
        accentColor: "text-amber-500",
      }
  }
}
