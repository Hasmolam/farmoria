#version 330

in vec2 in_position;
in vec2 in_texcoord;

uniform vec2 light_position;
uniform float light_radius;

out vec2 v_texcoord;
out vec2 v_position;

void main() {
    gl_Position = vec4(in_position, 0.0, 1.0);
    v_texcoord = in_texcoord;
    v_position = in_position;
} 