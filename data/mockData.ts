import type { Child, Stats, MedicalRecord, GrowthRecord } from "@/types"

const mockMedicalHistory: MedicalRecord[] = [
  {
    id: 1,
    date: "2024-01-15",
    weight: 15.2,
    height: 98,
    observations: "Desarrollo normal, buena alimentación",
    nutritionalStatus: "normal",
    vaccinations: ["BCG", "Hepatitis B", "DPT"],
    recommendations: "Continuar con alimentación balanceada",
  },
  {
    id: 2,
    date: "2023-12-10",
    weight: 14.8,
    height: 96,
    observations: "Ligero aumento de peso",
    nutritionalStatus: "normal",
    vaccinations: [],
    recommendations: "Aumentar actividad física",
  },
]

const mockGrowthHistory: GrowthRecord[] = [
  { date: "2024-01-15", weight: 15.2, height: 98, bmi: 15.8 },
  { date: "2023-12-10", weight: 14.8, height: 96, bmi: 16.1 },
  { date: "2023-11-05", weight: 14.5, height: 95, bmi: 16.1 },
  { date: "2023-10-01", weight: 14.2, height: 94, bmi: 16.1 },
]

export const mockChildren: Child[] = [
  {
    id: 1,
    name: "María González",
    age: "3 años",
    lastVisit: "2024-01-15",
    status: "normal",
    weight: 15.2,
    height: 98,
    community: "Villa Esperanza",
    birthDate: "2021-03-15",
    gender: "femenino",
    guardian: "Ana González",
    phone: "+57 300 123 4567",
    address: "Calle 15 #23-45",
    medicalHistory: mockMedicalHistory,
    growthHistory: mockGrowthHistory,
  },
  {
    id: 2,
    name: "Carlos Rodríguez",
    age: "7 años",
    lastVisit: "2024-01-10",
    status: "alerta",
    weight: 18.5,
    height: 110,
    community: "San José",
    birthDate: "2017-08-22",
    gender: "masculino",
    guardian: "Luis Rodríguez",
    phone: "+57 301 987 6543",
    address: "Carrera 8 #12-34",
    medicalHistory: [],
    growthHistory: [],
  },
  {
    id: 3,
    name: "Ana López",
    age: "5 años",
    lastVisit: "2024-01-08",
    status: "normal",
    weight: 17.8,
    height: 105,
    community: "Villa Esperanza",
    birthDate: "2019-05-10",
    gender: "femenino",
    guardian: "Carmen López",
    phone: "+57 302 456 7890",
    address: "Avenida 20 #45-67",
    medicalHistory: [],
    growthHistory: [],
  },
]

export const mockStats: Stats = {
  totalChildren: 156,
  monthlyFollowUps: 23,
  activeAlerts: 8,
  completedAssessments: 45,
}
