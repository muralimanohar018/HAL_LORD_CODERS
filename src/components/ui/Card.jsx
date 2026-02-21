import { motion, useMotionValue, useTransform } from "framer-motion";
import { useRef } from "react";

export default function Card({
  children,
  className = "",
  tilt = false,
  glow = false,
  glowColor = "blue",
  animate = true,
  delay = 0,
  onClick,
}) {
  const ref = useRef(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotateX = useTransform(y, [-50, 50], [4, -4]);
  const rotateY = useTransform(x, [-50, 50], [-4, 4]);

  const glowMap = {
    blue: "hover:shadow-glow",
    red: "hover:shadow-glow-red",
    amber: "hover:shadow-glow-amber",
    green: "hover:shadow-glow-green",
  };

  const handleMouseMove = (e) => {
    if (!tilt || !ref.current) return;
    const rect = ref.current.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    x.set(e.clientX - centerX);
    y.set(e.clientY - centerY);
  };

  const handleMouseLeave = () => {
    x.set(0);
    y.set(0);
  };

  const cardProps = tilt
    ? { style: { rotateX, rotateY, transformStyle: "preserve-3d" } }
    : {};

  return (
    <motion.div
      ref={ref}
      initial={animate ? { opacity: 0, y: 20 } : false}
      animate={animate ? { opacity: 1, y: 0 } : false}
      transition={{ duration: 0.5, delay, ease: "easeOut" }}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      {...cardProps}
      whileHover={!tilt ? { y: -6 } : {}}
      className={`
        glass rounded-2xl shadow-depth
        transition-all duration-300 ease-in-out
        ${glow ? glowMap[glowColor] : ""}
        ${onClick ? "cursor-pointer" : ""}
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
}
