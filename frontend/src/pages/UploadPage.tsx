import { useState } from "react"
import { FileUploader } from "@/components/FileUploader"
import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/buttons"

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const handleFileSelect = (selectedFile: File | null) => {
    setFile(selectedFile)
  }
  
  const handleSubmit = async () => {
    if (!file) return
    
    setIsSubmitting(true)
    
    // Simulate API call
    console.log("Uploading and analyzing file:", file.name)
    
    // In a real app, you would upload the file and get the analysis results
    setTimeout(() => {
      console.log("Analysis complete!")
      setIsSubmitting(false)
      // Navigate to results page
    }, 2000)
  }
  
  return (
    <div className="container mx-auto py-10">
      <div className="max-w-xl mx-auto">
        <div className="mb-8 space-y-4">
          <h1 className="text-3xl font-bold tracking-tight">Upload Contract</h1>
          <p className="text-muted-foreground">
            Upload a Solidity contract file (.sol) for security analysis
          </p>
        </div>
        
        <div className="space-y-8">
          <div className="bg-card border rounded-lg p-6">
            <FileUploader onFileSelect={handleFileSelect} />
          </div>
          
          <Button 
            onClick={handleSubmit}
            disabled={!file || isSubmitting}
            className="w-full"
          >
            {isSubmitting ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Analyzing...
              </>
            ) : (
              <>
                Analyze Contract
                <ArrowRight className="ml-2 h-4 w-4" />
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  )
}