import { motion } from "framer-motion";

const variants = {
  primary: `bg-gradient-to-r from-accent to-accent-dark text-white
    hover:shadow-glow hover:shadow-glow-lg border border-accent/30
    hover:border-accent`,
  secondary: `bg-transparent border border-border text-text-primary
    hover:border-accent hover:text-accent hover:shadow-glow`,
  danger: `bg-gradient-to-r from-high-risk to-red-700 text-white
    hover:shadow-glow-red border border-high-risk/30`,
  ghost: `bg-white/5 text-text-secondary hover:bg-white/10
    hover:text-text-primary border border-white/10`,
};

const sizes = {
  sm: "px-4 py-2 text-sm",
  md: "px-6 py-3 text-base",
  lg: "px-8 py-4 text-lg",
};

export default function Button({
  children,
  variant = "primary",
  size = "md",
  className = "",
  loading = false,
  icon,
  onClick,
  type = "button",
  disabled = false,
}) {
  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      whileHover={{ scale: 1.03, y: -2 }}
      whileTap={{ scale: 0.97 }}
      transition={{ duration: 0.15 }}
      className={`
        relative inline-flex items-center justify-center gap-2
        font-display font-semibold rounded-xl
        transition-all duration-300 ease-in-out
        cursor-pointer select-none outline-none
        disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none
        ${variants[variant]}
        ${sizes[size]}
        ${className}
      `}
    >
      {loading ? (
        <>
          <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
          <span>Processing...</span>
        </>
      ) : (
        <>
          {icon && <span className="flex-shrink-0">{icon}</span>}
          {children}
        </>
      )}
      {/* Shimmer overlay */}
      <span className="absolute inset-0 rounded-xl overflow-hidden pointer-events-none">
        <span className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-full hover:translate-x-full transition-transform duration-700" />
      </span>
    </motion.button>
  );
}
