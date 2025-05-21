import { useState, useCallback } from "react"
import { useDropzone } from "react-dropzone"
import { UploadCloud, File, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "./ui/buttons"

interface FileUploaderProps {
  onFileSelect?: (file: File | null) => void
}

export function FileUploader({ onFileSelect }: FileUploaderProps) {
  const [file, setFile] = useState<File | null>(null)
  
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles?.length > 0) {
      const selectedFile = acceptedFiles[0]
      setFile(selectedFile)
      
      if (onFileSelect) {
        onFileSelect(selectedFile)
      }
    }
  }, [onFileSelect])
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.sol'],
    },
    maxFiles: 1,
  })
  
  const removeFile = () => {
    setFile(null)
    if (onFileSelect) {
      onFileSelect(null)
    }
  }
  
  return (
    <div className="w-full">
      {!file ? (
        <div
          {...getRootProps()}
          className={cn(
            "border-2 border-dashed border-muted rounded-lg p-12 transition-colors flex flex-col items-center justify-center cursor-pointer",
            isDragActive && "border-primary/50 bg-primary/5"
          )}
        >
          <input {...getInputProps()} />
          <UploadCloud className="h-10 w-10 text-muted-foreground mb-4" />
          <p className="mb-2 text-sm text-muted-foreground text-center">
            <span className="font-semibold">Click to upload</span> or drag and drop
          </p>
          <p className="text-xs text-muted-foreground">
            Solidity files only (.sol)
          </p>
        </div>
      ) : (
        <div className="border rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-md bg-primary/10">
                <File className="h-5 w-5 text-primary" />
              </div>
              <div className="flex flex-col">
                <span className="text-sm font-medium">{file.name}</span>
                <span className="text-xs text-muted-foreground">
                  {(file.size / 1024).toFixed(2)} KB
                </span>
              </div>
            </div>
            <Button
              size="icon"
              variant="ghost"
              className="h-8 w-8 rounded-full"
              onClick={removeFile}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}