import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Shield, ArrowRight, Github, Upload, Code, FileCode, Zap } from "lucide-react"

export default function HomePage() {
  const navigate = useNavigate()
  const [file, setFile] = useState<File | null>(null)
  const [fileHover, setFileHover] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [isTestingDemo, setIsTestingDemo] = useState(false)
  const [errorMessage, setErrorMessage] = useState("")
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setErrorMessage("")
    }
  }
  
  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setFileHover(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      // Check if the file is a .sol file
      const droppedFile = e.dataTransfer.files[0]
      if (droppedFile.name.endsWith('.sol') || droppedFile.type === "text/plain") {
        setFile(droppedFile)
        setErrorMessage("")
      } else {
        setErrorMessage("Please upload a Solidity (.sol) file")
      }
    }
  }
  
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    setFileHover(true)
  }
  
  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    setFileHover(false)
  }
  
  const handleFileUpload = async () => {
    if (!file) {
      setErrorMessage("Please select a file first")
      return
    }
    
    setIsUploading(true)
    setErrorMessage("")
    
    try {
      // Create form data
      const formData = new FormData()
      formData.append('file', file)
      
      // Upload file to API
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })
      
      const data = await response.json()
      
      if (data.success) {
        // Navigate to report page
        navigate(`/report/${data.analysis_id}`)
      } else {
        setErrorMessage(data.error || "Upload failed. Please try again.")
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      setErrorMessage("Connection error. Please check if the API is running.")
    } finally {
      setIsUploading(false)
    }
  }
  
  const handleTestAnalysis = async () => {
    setIsTestingDemo(true)
    setErrorMessage("")
    
    try {
      // Call test analysis API
      const response = await fetch('/api/test-analysis')
      const data = await response.json()
      
      if (data.success) {
        // Navigate to report page
        navigate(`/report/${data.analysis_id}`)
      } else {
        setErrorMessage(data.error || "Test analysis failed. Please try again.")
      }
    } catch (error) {
      console.error('Error running test analysis:', error)
      setErrorMessage("Connection error. Please check if the API is running.")
    } finally {
      setIsTestingDemo(false)
    }
  }
  
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header/Navigation */}
      <header className="border-b border-border/40 bg-background">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center">
            <Shield className="h-6 w-6 text-primary" />
            <span className="ml-2 text-xl font-bold">SECURA</span>
          </div>
          <nav className="flex items-center space-x-4">
            <a
              href="https://github.com/yourusername/secura"
              target="_blank"
              rel="noreferrer"
              className="ml-4 inline-flex items-center space-x-1 text-sm font-medium text-muted-foreground hover:text-foreground"
            >
              <Github className="h-4 w-4" />
              <span>GitHub</span>
            </a>
          </nav>
        </div>
      </header>
      
      {/* Hero Section */}
      <section className="flex-1 flex flex-col items-center justify-center py-12 px-4">
        <div className="max-w-5xl w-full mx-auto grid gap-8 lg:grid-cols-2 lg:gap-16 items-center">
          <div>
            <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-6">
              Secure Your Smart Contracts with AI
            </h1>
            <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
              SECURA analyzes your Solidity contracts to find vulnerabilities, explain them clearly, and provide actionable fixes.
            </p>
            <div className="space-y-4">
              <button 
                onClick={handleTestAnalysis}
                disabled={isTestingDemo}
                className="w-full inline-flex items-center justify-center bg-primary text-primary-foreground px-6 py-3 rounded-md font-medium hover:bg-primary/90 disabled:opacity-70"
              >
                {isTestingDemo ? (
                  <>
                    <div className="mr-2 h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Running Demo Analysis...
                  </>
                ) : (
                  <>
                    <Zap className="mr-2 h-5 w-5" />
                    Try Demo Analysis
                  </>
                )}
              </button>
              <p className="text-sm text-muted-foreground text-center">
                Instantly analyze our sample Vulnerable.sol contract
              </p>
            </div>
          </div>
          
          {/* File Upload Card */}
          <div className="bg-card border rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold mb-4">
              Analyze Your Contract
            </h2>
            <div className="space-y-6">
              <div
                onDrop={handleFileDrop}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                className={`
                  border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
                  transition-colors duration-200
                  ${fileHover ? "border-primary/70 bg-primary/5" : "border-border"}
                  ${file ? "bg-primary/5" : ""}
                `}
              >
                <input
                  type="file"
                  id="contractFile"
                  accept=".sol"
                  onChange={handleFileChange}
                  className="hidden"
                />
                <label htmlFor="contractFile" className="cursor-pointer">
                  {!file ? (
                    <div className="flex flex-col items-center">
                      <Upload className="h-10 w-10 text-muted-foreground mb-4" />
                      <p className="mb-2 text-muted-foreground">
                        <span className="font-medium">Click to upload</span> or drag and drop
                      </p>
                      <p className="text-sm text-muted-foreground">
                        Solidity files only (.sol)
                      </p>
                    </div>
                  ) : (
                    <div className="flex items-center">
                      <FileCode className="h-8 w-8 text-primary mr-3" />
                      <div className="text-left">
                        <p className="font-medium truncate w-56">{file.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {(file.size / 1024).toFixed(2)} KB
                        </p>
                      </div>
                    </div>
                  )}
                </label>
              </div>
              
              {errorMessage && (
                <div className="bg-destructive/10 text-destructive px-4 py-2 rounded-md text-sm">
                  {errorMessage}
                </div>
              )}
              
              <div className="grid grid-cols-2 gap-4">
                <button
                  className="inline-flex items-center justify-center px-4 py-2 bg-secondary text-secondary-foreground rounded-md font-medium hover:bg-secondary/80"
                  onClick={() => navigate("/github-integration")}
                >
                  <Github className="mr-2 h-4 w-4" />
                  GitHub Repository
                </button>
                <button
                  onClick={handleFileUpload}
                  disabled={!file || isUploading}
                  className="inline-flex items-center justify-center px-4 py-2 bg-primary text-primary-foreground rounded-md font-medium hover:bg-primary/90 disabled:opacity-50 disabled:pointer-events-none"
                >
                  {isUploading ? (
                    <>
                      <div className="mr-2 h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      {file ? "Analyze Contract" : "Upload a File"}
                      {file && <ArrowRight className="ml-2 h-4 w-4" />}
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="bg-muted/30 py-16 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
          <div className="grid gap-8 md:grid-cols-3">
            <div className="bg-card border rounded-lg p-6">
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Shield className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Vulnerability Detection</h3>
              <p className="text-muted-foreground">
                Identify security issues like reentrancy, unchecked calls, and other common vulnerabilities.
              </p>
            </div>
            <div className="bg-card border rounded-lg p-6">
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center mb-4">

              </div>
              <h3 className="text-xl font-semibold mb-2">Developer Insights</h3>
              <p className="text-muted-foreground">
                Get expert recommendations on code quality, security patterns, and gas optimization.
              </p>
            </div>
            <div className="bg-card border rounded-lg p-6">
              <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              </div>
              <h3 className="text-xl font-semibold mb-2">AI Assistant</h3>
              <p className="text-muted-foreground">
                Chat with an AI expert about your contract's security issues and get detailed explanations.
              </p>
            </div>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="border-t border-border bg-background py-8 px-4">
        <div className="container mx-auto">
          <div className="flex flex-col sm:flex-row items-center justify-between">
            <div className="flex items-center mb-4 sm:mb-0">
              <Shield className="h-5 w-5 text-primary" />
              <span className="ml-2 font-semibold">SECURA</span>
            </div>
            <div className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} SECURA - Smart Contract Security Audit Tool
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}