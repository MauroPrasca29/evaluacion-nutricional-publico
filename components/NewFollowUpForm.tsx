"use client"

import { useState } from "react"
import { Save, Search, User, Camera, FileText, Activity } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Checkbox } from "@/components/ui/checkbox"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { FileUpload } from "./FileUpload"
import { FollowUpResults } from "./FollowUpResults"
import type { ThemeColors, FollowUpForm, Child } from "@/types"
import { SYMPTOMS_OPTIONS, PHYSICAL_SIGNS_OPTIONS } from "@/types"
import { mockChildren } from "@/data/mockData"

interface NewFollowUpFormProps {
  theme: ThemeColors
}

export function NewFollowUpForm({ theme }: NewFollowUpFormProps) {
  const [selectedChild, setSelectedChild] = useState<Child | null>(null)
  const [searchTerm, setSearchTerm] = useState("")
  const [showResults, setShowResults] = useState(false)
  const [formData, setFormData] = useState<FollowUpForm>({
    childId: 0,
    weight: "",
    height: "",
    armCircumference: "",
    headCircumference: "",
    tricepsFold: "",
    abdominalPerimeter: "",
    symptoms: [],
    physicalSigns: [],
    clinicalObservations: "",
    hemoglobin: "",
    stoolExam: "",
    urineExam: "",
    eyePhotos: [],
    gumPhotos: [],
    caregiverComments: "",
  })

  const filteredChildren = mockChildren.filter((child) => child.name.toLowerCase().includes(searchTerm.toLowerCase()))

  const calculateAge = (birthDate: string) => {
    const today = new Date()
    const birth = new Date(birthDate)
    const ageInMonths = (today.getFullYear() - birth.getFullYear()) * 12 + (today.getMonth() - birth.getMonth())
    const years = Math.floor(ageInMonths / 12)
    const months = ageInMonths % 12
    return `${years} años ${months} meses`
  }

  const calculateBMI = (weight: string, height: string) => {
    if (!weight || !height) return ""
    const weightNum = Number.parseFloat(weight)
    const heightNum = Number.parseFloat(height) / 100
    if (weightNum > 0 && heightNum > 0) {
      return (weightNum / (heightNum * heightNum)).toFixed(1)
    }
    return ""
  }

  const handleChildSelect = (child: Child) => {
    setSelectedChild(child)
    setFormData({ ...formData, childId: child.id })
    setSearchTerm("")
  }

  const handleSymptomChange = (symptom: string, checked: boolean) => {
    if (checked) {
      setFormData({ ...formData, symptoms: [...formData.symptoms, symptom] })
    } else {
      setFormData({ ...formData, symptoms: formData.symptoms.filter((s) => s !== symptom) })
    }
  }

  const handlePhysicalSignChange = (sign: string, checked: boolean) => {
    if (checked) {
      setFormData({ ...formData, physicalSigns: [...formData.physicalSigns, sign] })
    } else {
      setFormData({ ...formData, physicalSigns: formData.physicalSigns.filter((s) => s !== sign) })
    }
  }

  const handleEyePhotosChange = (files: File[]) => {
    setFormData({ ...formData, eyePhotos: files })
  }

  const handleGumPhotosChange = (files: File[]) => {
    setFormData({ ...formData, gumPhotos: files })
  }

  const handleSubmit = () => {
    if (!selectedChild) {
      alert("Por favor selecciona un niño")
      return
    }
    console.log("Seguimiento guardado:", formData)
    setShowResults(true)
  }

  const handleSaveToProfile = () => {
    // Aquí se guardaría en el perfil del niño
    console.log("Guardando en perfil del niño:", selectedChild?.id)
  }

  if (showResults && selectedChild) {
    return (
      <FollowUpResults
        child={selectedChild}
        followUpData={formData}
        theme={theme}
        onClose={() => setShowResults(false)}
        onSaveToProfile={handleSaveToProfile}
      />
    )
  }

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-slate-800 mb-3">Nuevo Seguimiento</h1>
        <p className="text-lg text-slate-600">Registra una nueva evaluación nutricional completa</p>
      </div>

      {/* Selección de niño */}
      {!selectedChild ? (
        <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
          <CardHeader>
            <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <User className="w-5 h-5" />
              Seleccionar Niño
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
              <Input
                placeholder="Buscar niño por nombre..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 border-amber-200 focus:border-amber-400"
              />
            </div>

            <div className="grid gap-3 max-h-60 overflow-y-auto">
              {filteredChildren.map((child) => (
                <div
                  key={child.id}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-slate-50 cursor-pointer transition-colors"
                  onClick={() => handleChildSelect(child)}
                >
                  <div className="flex items-center gap-3">
                    <Avatar className="w-10 h-10">
                      <AvatarFallback className="bg-gradient-to-br from-blue-400 to-blue-500 text-white font-bold text-sm">
                        {child.name
                          .split(" ")
                          .map((n) => n[0])
                          .join("")}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <h4 className="font-semibold text-slate-800">{child.name}</h4>
                      <p className="text-sm text-slate-600">
                        {calculateAge(child.birthDate)} • {child.community}
                      </p>
                    </div>
                  </div>
                  <Badge
                    className={`${
                      child.status === "normal" ? "bg-green-100 text-green-800" : "bg-orange-100 text-orange-800"
                    }`}
                  >
                    {child.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Niño seleccionado */}
          <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <Avatar className="w-12 h-12">
                    <AvatarFallback className="bg-gradient-to-br from-blue-400 to-blue-500 text-white font-bold">
                      {selectedChild.name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <h3 className="font-bold text-slate-800 text-lg">{selectedChild.name}</h3>
                    <p className="text-slate-600">
                      {calculateAge(selectedChild.birthDate)} • {selectedChild.community}
                    </p>
                  </div>
                </div>
                <Button
                  variant="outline"
                  onClick={() => setSelectedChild(null)}
                  className="hover:bg-red-50 hover:border-red-200 hover:text-red-600"
                >
                  Cambiar niño
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Formulario de seguimiento */}
          <div className="grid gap-8">
            {/* Datos Antropométricos */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br ${theme.cardBg} transition-all duration-500`}>
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  Datos Antropométricos
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="weight">Peso (kg) *</Label>
                    <Input
                      id="weight"
                      type="number"
                      step="0.1"
                      placeholder="15.2"
                      value={formData.weight}
                      onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="height">Talla / Estatura (cm) *</Label>
                    <Input
                      id="height"
                      type="number"
                      step="0.1"
                      placeholder="98.5"
                      value={formData.height}
                      onChange={(e) => setFormData({ ...formData, height: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="bmi">IMC (calculado automáticamente)</Label>
                    <Input
                      id="bmi"
                      value={calculateBMI(formData.weight, formData.height)}
                      readOnly
                      className="bg-gray-50 border-gray-200"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="age">Edad (calculado automáticamente)</Label>
                    <Input
                      id="age"
                      value={calculateAge(selectedChild.birthDate)}
                      readOnly
                      className="bg-gray-50 border-gray-200"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="armCircumference">Circunferencia Braquial (cm)</Label>
                    <Input
                      id="armCircumference"
                      type="number"
                      step="0.1"
                      placeholder="16.5"
                      value={formData.armCircumference}
                      onChange={(e) => setFormData({ ...formData, armCircumference: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="headCircumference">Perímetro Cefálico (cm)</Label>
                    <Input
                      id="headCircumference"
                      type="number"
                      step="0.1"
                      placeholder="48.2"
                      value={formData.headCircumference}
                      onChange={(e) => setFormData({ ...formData, headCircumference: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="tricepsFold">Pliegue Cutáneo Tricipital (mm)</Label>
                    <Input
                      id="tricepsFold"
                      type="number"
                      step="0.1"
                      placeholder="12.5"
                      value={formData.tricepsFold}
                      onChange={(e) => setFormData({ ...formData, tricepsFold: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="abdominalPerimeter">Perímetro Abdominal (cm)</Label>
                    <Input
                      id="abdominalPerimeter"
                      type="number"
                      step="0.1"
                      placeholder="52.3"
                      value={formData.abdominalPerimeter}
                      onChange={(e) => setFormData({ ...formData, abdominalPerimeter: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Observaciones Clínicas */}
            <Card className={`${theme.cardBorder} bg-gradient-to-br from-white to-blue-50 transition-all duration-500`}>
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Observaciones Clínicas Generales
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Síntomas */}
                <div className="space-y-3">
                  <Label className="text-base font-semibold">Síntomas observados o reportados</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {SYMPTOMS_OPTIONS.map((symptom) => (
                      <div key={symptom} className="flex items-center space-x-2">
                        <Checkbox
                          id={`symptom-${symptom}`}
                          checked={formData.symptoms.includes(symptom)}
                          onCheckedChange={(checked) => handleSymptomChange(symptom, checked as boolean)}
                        />
                        <Label htmlFor={`symptom-${symptom}`} className="text-sm">
                          {symptom}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Signos físicos */}
                <div className="space-y-3">
                  <Label className="text-base font-semibold">Signos físicos visibles</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {PHYSICAL_SIGNS_OPTIONS.map((sign) => (
                      <div key={sign} className="flex items-center space-x-2">
                        <Checkbox
                          id={`sign-${sign}`}
                          checked={formData.physicalSigns.includes(sign)}
                          onCheckedChange={(checked) => handlePhysicalSignChange(sign, checked as boolean)}
                        />
                        <Label htmlFor={`sign-${sign}`} className="text-sm">
                          {sign}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Observaciones adicionales */}
                <div className="space-y-2">
                  <Label htmlFor="clinicalObservations">Observaciones clínicas adicionales</Label>
                  <Textarea
                    id="clinicalObservations"
                    placeholder="Describe observaciones clínicas adicionales..."
                    value={formData.clinicalObservations}
                    onChange={(e) => setFormData({ ...formData, clinicalObservations: e.target.value })}
                    className="min-h-[100px] border-amber-200 focus:border-amber-400"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Exámenes Complementarios */}
            <Card
              className={`${theme.cardBorder} bg-gradient-to-br from-white to-green-50 transition-all duration-500`}
            >
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800">Exámenes Complementarios</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="hemoglobin">Hemoglobina (g/dL)</Label>
                    <Input
                      id="hemoglobin"
                      type="number"
                      step="0.1"
                      placeholder="12.5"
                      value={formData.hemoglobin}
                      onChange={(e) => setFormData({ ...formData, hemoglobin: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="stoolExam">Examen de heces</Label>
                    <Input
                      id="stoolExam"
                      placeholder="Resultado del examen"
                      value={formData.stoolExam}
                      onChange={(e) => setFormData({ ...formData, stoolExam: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="urineExam">Examen de orina</Label>
                    <Input
                      id="urineExam"
                      placeholder="Resultado del examen"
                      value={formData.urineExam}
                      onChange={(e) => setFormData({ ...formData, urineExam: e.target.value })}
                      className="border-amber-200 focus:border-amber-400"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Imágenes Clínicas */}
            <Card
              className={`${theme.cardBorder} bg-gradient-to-br from-white to-purple-50 transition-all duration-500`}
            >
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                  <Camera className="w-5 h-5" />
                  Imágenes Clínicas
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <FileUpload
                    id="eye-photos"
                    label="Foto de ojos"
                    accept="image/*"
                    multiple={true}
                    onFilesChange={handleEyePhotosChange}
                  />
                  <FileUpload
                    id="gum-photos"
                    label="Foto de encías"
                    accept="image/*"
                    multiple={true}
                    onFilesChange={handleGumPhotosChange}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Comentarios del Cuidador */}
            <Card
              className={`${theme.cardBorder} bg-gradient-to-br from-white to-orange-50 transition-all duration-500`}
            >
              <CardHeader>
                <CardTitle className="text-xl font-bold text-slate-800">Comentarios del Cuidador</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="caregiverComments">Observaciones y comentarios del cuidador</Label>
                  <Textarea
                    id="caregiverComments"
                    placeholder="Registra los comentarios, preocupaciones o observaciones del cuidador..."
                    value={formData.caregiverComments}
                    onChange={(e) => setFormData({ ...formData, caregiverComments: e.target.value })}
                    className="min-h-[120px] border-amber-200 focus:border-amber-400"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Botones de acción */}
            <div className="flex gap-4 justify-center pt-6">
              <Button
                onClick={handleSubmit}
                className={`px-8 py-3 bg-gradient-to-r ${theme.buttonColor} text-white font-semibold rounded-xl transition-all duration-300 hover:scale-105 shadow-lg`}
              >
                <Save className="w-5 h-5 mr-2" />
                Finalizar Seguimiento
              </Button>
              <Button
                variant="outline"
                className={`px-8 py-3 ${theme.cardBorder} hover:bg-opacity-50 bg-transparent transition-all duration-300 hover:scale-105 shadow-lg rounded-xl`}
              >
                Cancelar
              </Button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
