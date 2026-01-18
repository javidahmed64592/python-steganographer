// import Image from "next/image";

export default function NotFound() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center space-y-8">
      {/* Logo */}
      <div className="flex items-center space-x-4 mb-8">
        {/* <Image
          src="/logo.svg"
          alt="Python Steganographer Logo"
          width={64}
          height={64}
          className="neon-glow"
          priority
        /> */}
        <div className="text-2xl font-bold neon-glow text-[var(--text-primary)]">
          Python Steganographer
        </div>
      </div>

      {/* Error Message */}
      <div className="space-y-4">
        <h1 className="text-6xl font-bold text-[var(--neon-red)] neon-glow">
          404
        </h1>
        <h2 className="text-2xl font-semibold text-[var(--text-primary)]">
          Page Not Found
        </h2>
        <div className="max-w-md mx-auto space-y-2">
          <p className="text-[var(--text-secondary)]">
            The page you&apos;re looking for doesn&apos;t exist.
          </p>
          <p className="text-[var(--text-secondary)]">
            It might have been moved, deleted, or never existed.
          </p>
        </div>
      </div>
    </div>
  );
}
