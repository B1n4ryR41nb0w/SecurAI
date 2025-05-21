import { useState } from "react"
import { Link, useNavigate } from "react-router-dom"
import { Shield, Github, ArrowLeft, ArrowRight, Search, Code, FileCode } from "lucide-react"

export default function GitHubPage() {
  const navigate = useNavigate()
  const [repoUrl, setRepoUrl] = useState("")
  const [filePath, setFilePath] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [searchResults, setSearchResults] = useState<string[]>([])
  const [selectedFile, setSelectedFile] = useState("")
  const [errorMessage, setErrorMessage] = useState("")
  
  const handleSearch = () => {
    if (!repoUrl) {
      setErrorMessage("Please enter a GitHub repository URL")
      return
    }
    
    setIsLoading(true)
    
    // Simulate API call to search for Solidity files
    setTimeout(() => {
      // Mock results
      setSearchResults([
        "contracts/TokenSale.sol",
        "contracts/ERC20.sol",
        "contracts/Ownable.sol",
        "test/TestContract.sol"
      ])
      setErrorMessage("")
      setIsLoading(false)
    }, 1500)
  }
  
  const handleSubmit = () => {
    if (!selectedFile && !filePath) {
      setErrorMessage("Please select a Solidity file")
      return
    }
    
    // In a real app, you'd send this to your API
    // For now, just navigate to the report page
    navigate("/report/demo-analysis")
  }
  
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-background">
        <div className="container mx-auto flex h-16 items-center px-4">
          <Link to="/" className="flex items-center">
            <Shield className="h-6 w-6 text-primary mr-2" />
            <span className="text-xl font-bold">SECURA</span>
          </Link>
        </div>
      </header>
      
      <div className="container mx-auto py-10 px-4">
        <div className="max-w-3xl mx-auto">
          {/* Back link */}
          <div className="mb-8">
            <Link to="/" className="inline-flex items-center text-muted-foreground hover:text-foreground">
              <ArrowLeft className="h-4 w-4 mr-2" />
              <span>Back to Home</span>
            </Link>
          </div>
          
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-4">GitHub Repository</h1>
            <p className="text-muted-foreground">
              Analyze a Solidity smart contract from a GitHub repository.
            </p>
          </div>
          
          <div className="bg-card border rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Repository Details</h2>
            
            <div className="space-y-4">
              <div>
                <label htmlFor="repo-url" className="block text-sm font-medium mb-1">
                  Repository URL
                </label>
                <div className="flex">
                  <div className="relative flex-1">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <Github className="h-4 w-4 text-muted-foreground" />
                    </div>
                    <input
                      id="repo-url"
                      type="text"
                      className="bg-background border border-input rounded-l-md pl-10 pr-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-primary"
                      placeholder="https://github.com/username/repo"
                      value={repoUrl}
                      onChange={(e) => setRepoUrl(e.target.value)}
                    />
                  </div>
                  <button
                    onClick={handleSearch}
                    disabled={isLoading || !repoUrl}
                    className="bg-secondary text-secondary-foreground px-4 py-2 rounded-r-md font-medium hover:bg-secondary/80 disabled:opacity-50 flex items-center"
                  >
                    {isLoading ? (
                      <div className="h-4 w-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-2" />
                    ) : (
                      <Search className="h-4 w-4 mr-2" />
                    )}
                    Search
                  </button>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Example: https://github.com/OpenZeppelin/openzeppelin-contracts
                </p>
              </div>
              
              {/* Optional file path input */}
              <div>
                <label htmlFor="file-path" className="block text-sm font-medium mb-1">
                  File Path (Optional)
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                    <Code className="h-4 w-4 text-muted-foreground" />
                  </div>
                  <input
                    id="file-path"
                    type="text"
                    className="bg-background border border-input rounded-md pl-10 pr-4 py-2 w-full focus:outline-none focus:ring-2 focus:ring-primary"
                    placeholder="contracts/MyContract.sol"
                    value={filePath}
                    onChange={(e) => setFilePath(e.target.value)}
                  />
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Specify a particular file path or search for all Solidity files
                </p>
              </div>
              
              {errorMessage && (
                <div className="bg-destructive/10 text-destructive px-4 py-2 rounded-md text-sm">
                  {errorMessage}
                </div>
              )}
            </div>
          </div>
          
          {/* Search results */}
          {searchResults.length > 0 && (
            <div className="bg-card border rounded-lg p-6 mb-6">
              <h2 className="text-lg font-semibold mb-4">Found Solidity Files</h2>
              
              <div className="space-y-2 mb-4">
                {searchResults.map((file, index) => (
                  <div
                    key={index}
                    className={`border rounded-md p-3 cursor-pointer transition-colors ${
                      selectedFile === file
                        ? "border-primary bg-primary/5"
                        : "border-border hover:border-primary/50"
                    }`}
                    onClick={() => setSelectedFile(file)}
                  >
                    <div className="flex items-center">
                      <FileCode className="h-5 w-5 text-primary mr-3" />
                      <span className="font-medium">{file}</span>
                    </div>
                  </div>
                ))}
              </div>
              
              <button
                onClick={handleSubmit}
                disabled={!selectedFile && !filePath}
                className="w-full bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium hover:bg-primary/90 disabled:opacity-50 flex items-center justify-center"
              >
                Analyze Selected Contract
                <ArrowRight className="h-4 w-4 ml-2" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}