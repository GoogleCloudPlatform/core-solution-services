import { cn } from "../../src/lib/utils";

interface LoadingSpinnerProps extends React.HTMLAttributes<HTMLDivElement> {
  size?: "sm" | "md" | "lg";
}

const sizes = {
  sm: "w-4 h-4",
  md: "w-6 h-6",
  lg: "w-8 h-8",
};

export function LoadingSpinner({
  size = "md",
  className,
  ...props
}: LoadingSpinnerProps) {
  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn("relative inline-block", sizes[size], className)}
      {...props}
    >
      <svg
        className="w-full h-full"
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Static star shape - centered in larger viewBox */}
        <path
          d="M16 8L18.5 13L24 16L18.5 19L16 24L13.5 19L8 16L13.5 13L16 8Z"
          fill="rgb(216, 132, 234)"
          opacity="0.9"
        />
        {/* Rotating arc - with larger radius */}
        <path
          d="M16 4C8.26801 4 2 10.268 2 18"
          stroke="#E84B3C"
          strokeWidth="2"
          strokeLinecap="round"
          className="animate-[spin_1s_linear_infinite]"
          transform-origin="16 16"
        />
      </svg>
      <span className="sr-only">Loading...</span>
    </div>
  );
}