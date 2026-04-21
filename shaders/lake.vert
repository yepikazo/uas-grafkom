#version 330 core

layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aNormal;
layout(location = 2) in vec2 aTexCoord;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform float time;

out vec3 FragPos;
out vec3 Normal;
out vec2 TexCoord;

void main() {
    vec3 pos = aPos;

    // Animate wave using multiple sine waves
    float wave1 = sin(pos.x * 1.5 + time * 1.2) * 0.06;
    float wave2 = sin(pos.z * 2.0 + time * 0.8) * 0.04;
    float wave3 = sin((pos.x + pos.z) * 1.0 + time * 1.5) * 0.03;
    pos.y += wave1 + wave2 + wave3;

    // Recalculate normal based on wave derivatives
    float dx = 1.5 * cos(pos.x * 1.5 + time * 1.2) * 0.06
             + 1.0 * cos((pos.x + pos.z) * 1.0 + time * 1.5) * 0.03;
    float dz = 2.0 * cos(pos.z * 2.0 + time * 0.8) * 0.04
             + 1.0 * cos((pos.x + pos.z) * 1.0 + time * 1.5) * 0.03;

    vec3 waveNormal = normalize(vec3(-dx, 1.0, -dz));

    FragPos = vec3(model * vec4(pos, 1.0));
    Normal = mat3(transpose(inverse(model))) * waveNormal;
    TexCoord = aTexCoord;

    gl_Position = projection * view * model * vec4(pos, 1.0);
}
