export function GlassCard({ className = '', children, ...props }) {
  return (
    <div className={`glass p-6 ${className}`.trim()} {...props}>
      {children}
    </div>
  );
}
