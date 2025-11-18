import type { Child, Stats, MedicalRecord, GrowthRecord, GlobalBMIStats } from "@/types"

const detailedMedicalHistory: MedicalRecord[] = [
{
  id: 1,
  date: "2024-05-20",
  weight: 15.2,
  height: 98,
  bmi: 15.8,
  observations:
    "El niño presenta buen apetito y energía. Se observa un desarrollo psicomotor adecuado para su edad. La madre sigue las recomendaciones previas.",
  nutritionalStatus: "normal",
  vaccinations: ["Refuerzo DPT"],
  recommendations: {
    dietary: [
      "Continuar con dieta balanceada, rica en frutas y verduras.",
      "Asegurar 3 porciones de lácteos al día.",
      "Introducir pescado azul dos veces por semana.",
    ],
    general: ["Fomentar el juego al aire libre al menos 1 hora al día.", "Mantener rutina de sueño de 10-12 horas."],
  },
  alerts: [],
  professional: "Dr. Ana Castillo",
  reportId: "REP-0520-001",
},
{
  id: 2,
  date: "2024-02-10",
  weight: 14.5,
  height: 95,
  bmi: 16.1,
  observations:
    "Se detecta ligera palidez en mucosas. El niño ha tenido dos episodios de resfriado común en el último mes. Apetito selectivo, rechaza las verduras.",
  nutritionalStatus: "riesgo",
  vaccinations: [],
  recommendations: {
    dietary: [
      "Aumentar consumo de alimentos ricos en hierro: lentejas, espinacas, carne roja magra.",
      "Combinar alimentos ricos en hierro con fuentes de Vitamina C (naranja, fresas) para mejorar absorción.",
      "Ofrecer verduras de forma creativa (purés, tortillas).",
    ],
    general: ["Próximo control en 3 meses para reevaluar.", "Realizar hemograma si no hay mejoría."],
  },
  alerts: ["Riesgo de anemia ferropénica"],
  professional: "Dr. Ana Castillo",
  reportId: "REP-0210-001",
},
{
  id: 3,
  date: "2023-11-05",
  weight: 14.2,
  height: 94,
  bmi: 16.1,
  observations: "Consulta de control. Desarrollo normal, sin signos de alarma.",
  nutritionalStatus: "normal",
  vaccinations: ["BCG", "Hepatitis B"],
  recommendations: {
    dietary: ["Mantener la lactancia materna complementada con alimentación sólida variada."],
    general: ["Vigilar la aparición de los primeros molares."],
  },
  alerts: [],
  professional: "Dr. Ana Castillo",
  reportId: "REP-1105-001",
},
]

const mockGrowthHistory: GrowthRecord[] = [
{ date: "2024-05-20", weight: 15.2, height: 98, bmi: 15.8 },
{ date: "2024-02-10", weight: 14.5, height: 95, bmi: 16.1 },
{ date: "2023-11-05", weight: 14.2, height: 94, bmi: 16.1 },
{ date: "2023-08-01", weight: 13.8, height: 92, bmi: 16.3 },
]

export const mockChildren: Child[] = [
{
  id: 1,
  name: "María González",
  age: "3 años",
  lastVisit: "2024-05-20",
  status: "normal",
  weight: 15.2,
  height: 98,
  community: "Villa Esperanza",
  birthDate: "2021-03-15",
  gender: "femenino",
  guardian: "Ana González",
  phone: "+57 300 123 4567",
  address: "Calle 15 #23-45",
  medicalHistory: detailedMedicalHistory,
  growthHistory: mockGrowthHistory,
},
{
  id: 2,
  name: "Carlos Rodríguez",
  age: "7 años",
  lastVisit: "2024-04-18",
  status: "alerta",
  weight: 18.5,
  height: 110,
  community: "San José",
  birthDate: "2017-08-22",
  gender: "masculino",
  guardian: "Luis Rodríguez",
  phone: "+57 301 987 6543",
  address: "Carrera 8 #12-34",
  medicalHistory: [
    {
      id: 4,
      date: "2024-04-18",
      weight: 18.5,
      height: 110,
      bmi: 15.3,
      observations:
        "El niño muestra un peso muy bajo para su talla y edad. Se observa apatía y pérdida de masa muscular en brazos y piernas.",
      nutritionalStatus: "severo",
      vaccinations: [],
      recommendations: {
        dietary: [
          "Iniciar suplemento nutricional hipercalórico de inmediato.",
          "Dieta fraccionada: 6 comidas pequeñas y nutritivas al día.",
          "Aumentar densidad calórica de las comidas (añadir aceite de oliva, aguacate).",
        ],
        general: [
          "Derivación urgente a pediatría para descartar patologías subyacentes.",
          "Control semanal estricto de peso.",
        ],
      },
      alerts: ["Desnutrición aguda severa", "Requiere intervención médica urgente"],
      professional: "Dr. Carlos Mendoza",
      reportId: "REP-0418-002",
    },
  ],
  growthHistory: [{ date: "2024-04-18", weight: 18.5, height: 110, bmi: 15.3 }],
},
{
  id: 3,
  name: "Ana López",
  age: "5 años",
  lastVisit: "2024-05-15",
  status: "normal",
  weight: 20.5,
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
totalChildren: 238,
monthlyFollowUps: 42,
activeAlerts: 19,
completedAssessments: 157,
pendingAssessments: 25,
}

export const mockGlobalBMIStats: GlobalBMIStats = {
"0-5": {
  severeUnderweight: 8, 
  underweight: 15, 
  normal: 85, 
  overweight: 12, 
  obesity: 5, 
},
"6-11": {
  severeUnderweight: 4, 
  underweight: 11, 
  normal: 72, 
  overweight: 18, 
  obesity: 8, 
},
}

export const mockAppointments = [
{
  id: 1,
  child: "Laura Jiménez",
  time: "10:00 AM",
  type: "Seguimiento",
  date: "2024-07-29",
},
{
  id: 2,
  child: "Pedro Marín",
  time: "11:30 AM",
  type: "Primera Consulta",
  date: "2024-07-29",
},
{
  id: 3,
  child: "Sofía Castro",
  time: "02:00 PM",
  type: "Seguimiento",
  date: "2024-07-29",
},
{
  id: 4,
  child: "Mateo Gómez",
  time: "09:00 AM",
  type: "Control de Alerta",
  date: "2024-07-30",
},
]

export const mockRecentActivity = [
{
  id: 1,
  icon: "user-plus",
  text: "Nuevo niño registrado:",
  subject: "David Rivas",
  time: "Hace 2 horas",
},
{
  id: 2,
  icon: "file-text",
  text: "Seguimiento completado para",
  subject: "Valeria López",
  time: "Ayer",
},
{
  id: 3,
  icon: "alert-triangle",
  text: "Nueva alerta de sobrepeso para",
  subject: "Samuel Castro",
  time: "Ayer",
},
{
  id: 4,
  icon: "upload",
  text: "Importación de datos completada",
  subject: "Sede San José",
  time: "Hace 2 días",
},
]
