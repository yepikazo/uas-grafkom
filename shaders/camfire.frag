#version 330 core

in vec3 Color;
in float Life;
in float PointSize;

out vec4 FragColor;

void main() {
    // Create circular particles
    vec2 center = gl_PointCoord - vec2(0.5);
    float dist = length(center);
    if (dist > 0.5) discard;

    // Soft glow with falloff
    float alpha = (1.0 - dist * 2.0) * Life;
    alpha = pow(alpha, 0.8);

    // Brighter center
    vec3 glowColor = Color + vec3(0.3, 0.15, 0.0) * (1.0 - dist * 2.0);

    FragColor = vec4(glowColor, alpha * 0.9);
}
