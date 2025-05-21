 import { Link } from "react-router-dom"
import { Shield, Github, Menu, X } from "lucide-react"
import { useState } from "react"
import { cn } from "@/lib/utils"

export function Navbar() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center">
        <div className="mr-4 flex">
          <Link to="/" className="mr-6 flex items-center space-x-2">
            <Shield className="h-6 w-6 text-primary" />
            <span className="hidden font-bold sm:inline-block">
              SECURA
            </span>
          </Link>
          <nav className="hidden md:flex items-center space-x-6 text-sm font-medium">
            <Link
              to="/"
              className="transition-colors hover:text-foreground/80 text-foreground"
            >
              Home
            </Link>
            <Link
              to="/upload"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Audit
            </Link>
            <Link
              to="/docs"
              className="transition-colors hover:text-foreground/80 text-foreground/60"
            >
              Documentation
            </Link>
          </nav>
        </div>

        {/* Mobile menu button */}
        <button
          className="inline-flex items-center justify-center md:hidden ml-auto"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          {isMenuOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}
        </button>

        {/* Desktop right nav */}
        <div className="hidden md:flex flex-1 items-center justify-end space-x-4">
          <nav className="flex items-center space-x-2">
            <a
              href="https://github.com/yourusername/secura"
              target="_blank"
              rel="noreferrer"
              className="inline-flex h-9 items-center justify-center rounded-md px-3 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
            >
              <Github className="h-4 w-4 mr-2" />
              GitHub
            </a>
          </nav>
        </div>
      </div>

      {/* Mobile menu */}
      <div className={cn(
        "md:hidden container overflow-hidden transition-all",
        isMenuOpen ? "max-h-64" : "max-h-0"
      )}>
        <nav className="flex flex-col space-y-4 py-4">
          <Link
            to="/"
            className="px-2 py-1 text-foreground transition-colors hover:text-foreground/80"
            onClick={() => setIsMenuOpen(false)}
          >
            Home
          </Link>
          <Link
            to="/upload"
            className="px-2 py-1 text-foreground/60 transition-colors hover:text-foreground/80"
            onClick={() => setIsMenuOpen(false)}
          >
            Audit
          </Link>
          <Link
            to="/docs"
            className="px-2 py-1 text-foreground/60 transition-colors hover:text-foreground/80"
            onClick={() => setIsMenuOpen(false)}
          >
            Documentation
          </Link>
          <a
            href="https://github.com/yourusername/secura"
            target="_blank"
            rel="noreferrer"
            className="px-2 py-1 flex items-center text-foreground/60 transition-colors hover:text-foreground/80"
            onClick={() => setIsMenuOpen(false)}
          >
            <Github className="h-4 w-4 mr-2" />
            GitHub
          </a>
        </nav>
      </div>
    </header>
  )
}