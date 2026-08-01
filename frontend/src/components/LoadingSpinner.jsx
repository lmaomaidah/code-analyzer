export default function LoadingSpinner() {
  return (
    <div style={{
      width: 24, height: 24,
      border: '3px solid #1E3A54',
      borderTop: '3px solid #14C9A8',
      borderRadius: '50%',
      animation: 'spin 0.8s linear infinite'
    }} />
  )
}