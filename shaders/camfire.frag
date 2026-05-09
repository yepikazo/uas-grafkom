#version 330 core

in vec3 Color;     // "birth color" — hottest color of this particle
in float Life;     // normalised life ratio [0..1]
in float PointSize;

out vec4 FragColor;

void main() {
    // ── Radial coordinate ──────────────────────────────────────────────────
    vec2 uv = gl_PointCoord - vec2(0.5);   // [-0.5 .. 0.5]
    float dist = length(uv);               // 0 = centre, 0.5 = edge
    if (dist > 0.5) discard;

    float r = dist * 2.0;                  // normalised radius [0..1]

    // ── Tutorial-style multi-layer alpha glow ─────────────────────────────
    // Direct port of the tutorial's alpha_layers loop:
    //   for i in range(alpha_layers, -1, -1):
    //       alpha = 255 - i * gap
    //       radius = r * i * i * glow_constant
    // We use 3 layers, each a soft concentric falloff.
    float a1 = max(0.0, 1.0 - r / 0.38);         // tight bright core
    float a2 = max(0.0, 1.0 - r / 0.68) * 0.55;  // mid glow ring
    float a3 = max(0.0, 1.0 - r / 1.00) * 0.25;  // outer haze
    float alpha = clamp(a1 + a2 + a3, 0.0, 1.0);

    // ── Tutorial-style color shift as particle "shrinks" (life decreases) ──
    // Tutorial: r==4,3 → red; r==2 → orange; r==1 → gray (smoke)
    // We map: Life=1.0 → birth color (hot);
    //         Life=0.5 → orange mid-tone;
    //         Life=0.2 → deep red ember;
    //         Life=0.0 → dark smoke gray
    vec3 orangeMid  = vec3(1.0,  0.38, 0.02);
    vec3 deepRed    = vec3(0.72, 0.10, 0.01);
    vec3 smokeGray  = vec3(0.07, 0.06, 0.06);

    vec3 finalColor;
    if (Life > 0.6) {
        // Hot birth phase → blend birth color toward orange
        float t = (Life - 0.6) / 0.4;           // 1=birth, 0=orange onset
        finalColor = mix(orangeMid, Color, t);
    } else if (Life > 0.25) {
        // Cooling phase: orange → deep red
        float t = (Life - 0.25) / 0.35;
        finalColor = mix(deepRed, orangeMid, t);
    } else {
        // Dying: ember red → dark smoke
        float t = Life / 0.25;
        finalColor = mix(smokeGray, deepRed, t);
    }

    // Brighten the very centre (hot-spot, mimics tutorial's innermost ring)
    float hotspot = max(0.0, 1.0 - r / 0.22);
    finalColor += vec3(0.35, 0.18, 0.0) * hotspot;

    // Multiply alpha by life so dying particles fade out gracefully
    alpha *= Life * 0.95;

    FragColor = vec4(finalColor, alpha);
}
