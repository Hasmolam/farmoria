#version 330

in vec2 in_position;
in vec2 in_texcoord;

uniform vec4 tint_color;

out vec2 v_texcoord;
out vec4 v_color;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    v_texcoord = in_texcoord;
    v_color = tint_color;
} 