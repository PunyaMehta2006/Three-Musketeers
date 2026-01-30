import React, { useCallback } from 'react';
import Particles from "react-particles";
import { loadSlim } from "tsparticles-slim";

const NetworkBackground = () => {

  const particlesInit = useCallback(async engine => {
    await loadSlim(engine);
  }, []);

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      className="absolute inset-0 -z-0"
      options={{
        fullScreen: { enable: false },
        background: {
          color: { value: "transparent" }
        },
        fpsLimit: 120,
        interactivity: {
          events: {
            onHover: {
              enable: true,
              mode: "grab"
            },
            resize: true
          },
          modes: {
            grab: {
              distance: 150,
              links: { opacity: 0.5 }
            }
          }
        },
        particles: {
          color: {
            value: "#475569"
          },
          links: {
            color: "#94a3b8",
            distance: 150,
            enable: true,
            opacity: 0.2,
            width: 1
          },
          move: {
            enable: true,
            speed: 0.5,
            direction: "none",
            random: false,
            straight: false,
            outModes: { default: "bounce" }
          },
          number: {
            density: { enable: true, area: 800 },
            value: 150
          },
          opacity: {
            value: 0.5
          },
          shape: {
            type: "circle"
          },
          size: {
            value: { min: 1, max: 4 }
          }
        },
        detectRetina: true
      }}
    />
  );
};

export default NetworkBackground;