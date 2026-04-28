#version 330 core

in vec3  vColor;
in float vBrightness;

out vec4 FragColor;

void main() {
    // Circular point sprite — discard corners
    vec2  center = gl_PointCoord - vec2(0.5);
    float dist   = length(center);
    if (dist > 0.5) discard;

    // Radial glow: bright white core fading to the firefly's color at edges
    float coreFactor = 1.0 - smoothstep(0.0, 0.25, dist);   // tight bright core
    float glowFactor = 1.0 - smoothstep(0.0, 0.50, dist);   // soft outer glow

    // Core is near-white, edge is the firefly color
    vec3 coreColor = mix(vColor, vec3(1.0, 1.0, 0.85), coreFactor * 0.8);
    vec3 finalColor = coreColor;

    // Alpha: full at center, zero at edge, modulated by blink brightness
    float alpha = glowFactor * glowFactor * vBrightness;

    // Discard fully dark fireflies so they don't z-fight when off
    if (alpha < 0.01) discard;

    FragColor = vec4(finalColor, alpha);
}
