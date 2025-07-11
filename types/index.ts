export interface Child {
  id: number
  name: string
  age: string
  lastVisit: string
  status: "normal" | "alerta"
  weight: number
  height: number
  community: string
  birthDate: string
  gender: "masculino" | "femenino"
  guardian: string
  phone: string
  address: string
  medicalHistory: MedicalRecord[]
  growthHistory: GrowthRecord[]
}

export interface MedicalRecord {
  id: number
  date: string
  weight: number
  height: number
  observations: string
  nutritionalStatus: "normal" | "alerta" | "seguimiento"
  vaccinations: string[]
  recommendations: string
}

export interface GrowthRecord {
  date: string
  weight: number
  height: number
  bmi: number
}

export interface Stats {
  totalChildren: number
  monthlyFollowUps: number
  activeAlerts: number
  completedAssessments: number
}

export interface ThemeColors {
  gradient: string
  headerBg: string
  headerBorder: string
  cardBorder: string
  cardBorder2?: string
  cardBg: string
  buttonColor: string
  accentColor: string
}

export interface MenuItem {
  id: string
  label: string
  icon: any
  color: string
  bgColor: string
  hoverColor: string
  borderColor: string
}

export interface NewChildForm {
  name: string
  birthDate: string
  gender: "masculino" | "femenino" | ""
  guardian: string
  phone: string
  address: string
  community: string
  weight: string
  height: string
  observations: string
}

export interface FollowUpForm {
  childId: number
  // Datos antropométricos
  weight: string
  height: string
  armCircumference: string
  headCircumference: string
  tricepsFold: string
  abdominalPerimeter: string
  // Observaciones clínicas
  symptoms: string[]
  physicalSigns: string[]
  clinicalObservations: string
  // Exámenes complementarios
  hemoglobin: string
  stoolExam: string
  urineExam: string
  // Imágenes clínicas
  eyePhotos: File[]
  gumPhotos: File[]
  // Comentarios del cuidador
  caregiverComments: string
}

export const SYMPTOMS_OPTIONS = [
  "Pérdida de apetito",
  "Fatiga o debilidad",
  "Irritabilidad",
  "Dificultad para concentrarse",
  "Problemas de sueño",
  "Dolor abdominal",
  "Náuseas o vómitos",
  "Diarrea",
  "Estreñimiento",
  "Fiebre",
  "Dolor de cabeza",
  "Mareos",
]

export const PHYSICAL_SIGNS_OPTIONS = [
  "Palidez en piel o mucosas",
  "Cabello quebradizo o decolorado",
  "Uñas frágiles o con manchas",
  "Retraso en el crecimiento",
  "Pérdida de masa muscular",
  "Acumulación de grasa abdominal",
  "Edema (hinchazón)",
  "Lesiones en la piel",
  "Problemas dentales",
  "Ojos hundidos",
  "Abdomen distendido",
  "Extremidades delgadas",
]
