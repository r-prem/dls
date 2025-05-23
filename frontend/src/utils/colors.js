export function generateColorRange(hexColor) {
  // Convert hex to RGB
  const r = parseInt(hexColor.slice(1, 3), 16)
  const g = parseInt(hexColor.slice(3, 5), 16)
  const b = parseInt(hexColor.slice(5, 7), 16)

  // Generate 9 shades from light to dark
  const colors = {}
  for (let i = 1; i <= 9; i++) {
    // Calculate the shade factor (0.1 to 0.9)
    const factor = i / 10
    
    // Generate the shade
    const shadeR = Math.round(r * factor)
    const shadeG = Math.round(g * factor)
    const shadeB = Math.round(b * factor)
    
    // Convert back to hex
    const shadeHex = `#${shadeR.toString(16).padStart(2, '0')}${shadeG.toString(16).padStart(2, '0')}${shadeB.toString(16).padStart(2, '0')}`
    
    if(i === 7) {
      colors[`--surface-gray-${i}`] = hexColor
    } else {
      colors[`--surface-gray-${i}`] = shadeHex
    }

  }

  return colors
}

export function injectPrimaryColorVariables(primaryColor) {
  if (!primaryColor) return
  const colors = generateColorRange(primaryColor)
  let styleElement = document.getElementById('primary-color-variables')
  if (!styleElement) {
    styleElement = document.createElement('style')
    styleElement.id = 'primary-color-variables'
    document.head.appendChild(styleElement)
  }
  styleElement.textContent = `
    button.bg-surface-gray-7,
    div.bg-surface-gray-7.rounded-full.h-1 {
      ${Object.entries(colors).map(([key, value]) => `${key}: ${value};`).join('\n')}
    }
  `
} 