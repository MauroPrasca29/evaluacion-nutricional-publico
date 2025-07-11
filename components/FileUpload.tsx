"use client"

import type React from "react"

import { useState } from "react"
import { Upload, X, FileImage, File } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"

interface FileUploadProps {
  id: string
  label: string
  accept?: string
  multiple?: boolean
  onFilesChange: (files: File[]) => void
  className?: string
}

export function FileUpload({ id, label, accept = "*/*", multiple = false, onFilesChange, className }: FileUploadProps) {
  const [files, setFiles] = useState<File[]>([])
  const [dragOver, setDragOver] = useState(false)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || [])
    const newFiles = multiple ? [...files, ...selectedFiles] : selectedFiles
    setFiles(newFiles)
    onFilesChange(newFiles)
  }

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault()
    setDragOver(false)
    const droppedFiles = Array.from(event.dataTransfer.files)
    const newFiles = multiple ? [...files, ...droppedFiles] : droppedFiles
    setFiles(newFiles)
    onFilesChange(newFiles)
  }

  const removeFile = (index: number) => {
    const newFiles = files.filter((_, i) => i !== index)
    setFiles(newFiles)
    onFilesChange(newFiles)
  }

  const isImage = (file: File) => file.type.startsWith("image/")

  return (
    <div className={`space-y-3 ${className}`}>
      <Label htmlFor={id}>{label}</Label>

      {/* Drop zone */}
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragOver ? "border-amber-400 bg-amber-50" : "border-amber-200 hover:border-amber-300 hover:bg-amber-50/50"
        }`}
        onDragOver={(e) => {
          e.preventDefault()
          setDragOver(true)
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <Upload className="w-8 h-8 text-amber-400 mx-auto mb-2" />
        <p className="text-sm text-slate-600 mb-2">Arrastra archivos aquí o haz clic para seleccionar</p>
        <input id={id} type="file" accept={accept} multiple={multiple} onChange={handleFileChange} className="hidden" />
        <Button
          type="button"
          variant="outline"
          onClick={() => document.getElementById(id)?.click()}
          className="border-amber-200 hover:border-amber-400"
        >
          Seleccionar archivos
        </Button>
      </div>

      {/* File previews */}
      {files.length > 0 && (
        <div className="space-y-2">
          <Label className="text-sm font-medium">Archivos seleccionados:</Label>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {files.map((file, index) => (
              <div key={index} className="relative group">
                <div className="border border-slate-200 rounded-lg p-3 bg-white hover:shadow-md transition-shadow">
                  <div className="flex items-center gap-3">
                    {isImage(file) ? (
                      <div className="relative">
                        <img
                          src={URL.createObjectURL(file) || "/placeholder.svg"}
                          alt={file.name}
                          className="w-12 h-12 object-cover rounded"
                        />
                        <FileImage className="absolute -top-1 -right-1 w-4 h-4 text-blue-500 bg-white rounded-full p-0.5" />
                      </div>
                    ) : (
                      <div className="w-12 h-12 bg-slate-100 rounded flex items-center justify-center">
                        <File className="w-6 h-6 text-slate-500" />
                      </div>
                    )}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-800 truncate">{file.name}</p>
                      <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                  </div>

                  {/* Delete button */}
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(index)}
                    className="absolute -top-2 -right-2 w-6 h-6 p-0 bg-red-500 hover:bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
