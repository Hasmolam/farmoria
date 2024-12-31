#version 330

uniform sampler2D texture0;
uniform vec2 resolution;
uniform float blur_radius;

in vec2 v_texcoord;
out vec4 f_color;

void main() {
    vec4 color = vec4(0.0);
    float total_weight = 0.0;
    
    // Gaussian blur
    for (float x = -blur_radius; x <= blur_radius; x += 1.0) {
        for (float y = -blur_radius; y <= blur_radius; y += 1.0) {
            vec2 offset = vec2(x, y) / resolution;
            float weight = exp(-(x*x + y*y) / (2.0 * blur_radius * blur_radius));
            color += texture(texture0, v_texcoord + offset) * weight;
            total_weight += weight;
        }
    }
    
    f_color = color / total_weight;
} 