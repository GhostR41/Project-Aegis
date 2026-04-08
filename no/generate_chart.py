import os

svg_data = """<svg viewBox="0 0 800 400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#4FC3F7" stop-opacity="0.8" />
      <stop offset="100%" stop-color="#4FC3F7" stop-opacity="0" />
    </linearGradient>
    <filter id="glow">
        <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
        <feMerge>
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>
    </filter>
  </defs>
  <rect width="100%" height="100%" fill="transparent" />
  
  <!-- Grid Lines -->
  <line x1="50" y1="350" x2="750" y2="350" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
  <line x1="50" y1="275" x2="750" y2="275" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
  <line x1="50" y1="200" x2="750" y2="200" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
  <line x1="50" y1="125" x2="750" y2="125" stroke="rgba(255,255,255,0.05)" stroke-width="1"/>
  
  <text x="30" y="355" fill="rgba(255,255,255,0.4)" font-family="monospace" font-size="12" text-anchor="end">0</text>
  <text x="30" y="280" fill="rgba(255,255,255,0.4)" font-family="monospace" font-size="12" text-anchor="end">10K</text>
  <text x="30" y="205" fill="rgba(255,255,255,0.4)" font-family="monospace" font-size="12" text-anchor="end">20K</text>
  <text x="30" y="130" fill="rgba(255,255,255,0.4)" font-family="monospace" font-size="12" text-anchor="end">30K</text>
  <text x="30" y="55" fill="rgba(255,255,255,0.4)" font-family="monospace" font-size="12" text-anchor="end">40K</text>
  
  <!-- Horizontal Axis Labels -->
  <text x="100" y="375" fill="rgba(255,255,255,0.6)" font-family="monospace" font-size="14" text-anchor="middle">1990</text>
  <text x="250" y="375" fill="rgba(255,255,255,0.6)" font-family="monospace" font-size="14" text-anchor="middle">2000</text>
  <text x="400" y="375" fill="rgba(255,255,255,0.6)" font-family="monospace" font-size="14" text-anchor="middle">2010</text>
  <text x="550" y="375" fill="rgba(255,255,255,0.6)" font-family="monospace" font-size="14" text-anchor="middle">2020</text>
  <text x="700" y="375" fill="rgba(255,255,255,0.6)" font-family="monospace" font-size="14" text-anchor="middle">2024</text>
  
  <!-- Data Area -->
  <polygon points="100,350 250,335 400,275 550,162.5 700,72 700,350 100,350" fill="url(#gradient)" />
  
  <!-- Data Line -->
  <!-- 1990: <500 (y=346), 2000:~2000 (y=335), 2010:~10000(y=275), 2020:~25000(y=162.5), 2024:~37000(y=72) (scale: 10k = 75px, max 40k = 300px, 350-val) -->
  <polyline points="100,346 250,335 400,275 550,162.5 700,72.5" fill="none" stroke="#4FC3F7" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>
  
  <!-- Data Points -->
  <circle cx="100" cy="346" r="6" fill="#000" stroke="#4FC3F7" stroke-width="2" />
  <circle cx="250" cy="335" r="6" fill="#000" stroke="#4FC3F7" stroke-width="2" />
  <circle cx="400" cy="275" r="6" fill="#000" stroke="#4FC3F7" stroke-width="2" />
  <circle cx="550" cy="162.5" r="6" fill="#000" stroke="#4FC3F7" stroke-width="2" />
  <circle cx="700" cy="72.5" r="6" fill="#000" stroke="#4FC3F7" stroke-width="2" />
</svg>
"""

os.makedirs('public/media/data', exist_ok=True)
with open('public/media/data/discovery_chart.svg', 'w') as f:
    f.write(svg_data)
print("Data chart generated successfully.")
