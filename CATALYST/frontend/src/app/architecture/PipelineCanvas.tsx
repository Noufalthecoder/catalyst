'use client';

import React, { Suspense, useRef, useMemo, useState, useCallback, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, Float, MeshTransmissionMaterial, Environment } from '@react-three/drei';
import * as THREE from 'three';

/* ─── Types ─────────────────────────────────────────────────────────────────── */
interface Stage {
  id: string;
  num: string;
  title: string;
  subtitle: string;
  metric: string;
  status: string;
  color: string;
  accent: string;
  desc: string;
  details: { label: string; value: string }[];
}

interface Props {
  stages: Stage[];
  activeStage: number;
  selectedStage: number | null;
  onSelectStage: (idx: number | null) => void;
  showWow: boolean;
}

/* ─── Constants ──────────────────────────────────────────────────────────────── */
const STAGE_SPACING = 4.5;
const STAGE_START_Z = 0;
const STAGE_W = 3.2;
const STAGE_H = 1.6;
const STAGE_D = 0.18;

/* ─── Helpers ────────────────────────────────────────────────────────────────── */
function hexToVec3(hex: string): THREE.Color {
  return new THREE.Color(hex);
}

/* ─── Particle Field ─────────────────────────────────────────────────────────── */
function ParticleField({ stageCount }: { stageCount: number }) {
  const meshRef = useRef<THREE.Points>(null!);
  const count = 600;

  const [positions, colors] = useMemo(() => {
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    const palette = [
      new THREE.Color('#2F6BFF'),
      new THREE.Color('#06B6D4'),
      new THREE.Color('#62E6A7'),
      new THREE.Color('#8B5CF6'),
      new THREE.Color('#F5B84B'),
    ];
    for (let i = 0; i < count; i++) {
      const totalLen = stageCount * STAGE_SPACING;
      pos[i * 3] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 14;
      pos[i * 3 + 2] = -(Math.random() * totalLen + 4);
      const c = palette[Math.floor(Math.random() * palette.length)];
      col[i * 3] = c.r;
      col[i * 3 + 1] = c.g;
      col[i * 3 + 2] = c.b;
    }
    return [pos, col];
  }, [stageCount]);

  useFrame((_, delta) => {
    if (!meshRef.current) return;
    meshRef.current.rotation.y += delta * 0.012;
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" args={[positions, 3]} />
        <bufferAttribute attach="attributes-color" args={[colors, 3]} />
      </bufferGeometry>
      <pointsMaterial size={0.035} vertexColors transparent opacity={0.35} sizeAttenuation />
    </points>
  );
}

/* ─── Data Flow Beam ─────────────────────────────────────────────────────────── */
function DataBeam({
  from,
  to,
  color,
  active,
}: {
  from: THREE.Vector3;
  to: THREE.Vector3;
  color: string;
  active: boolean;
}) {
  const ref = useRef<THREE.Mesh>(null!);
  const mid = from.clone().add(to).multiplyScalar(0.5);
  const dir = to.clone().sub(from);
  const length = dir.length();
  const quat = new THREE.Quaternion();
  quat.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().normalize());

  useFrame(({ clock }) => {
    if (!ref.current) return;
    const mat = ref.current.material as THREE.MeshBasicMaterial;
    mat.opacity = active ? 0.55 + Math.sin(clock.elapsedTime * 4) * 0.25 : 0.12;
  });

  return (
    <mesh ref={ref} position={mid} quaternion={quat}>
      <cylinderGeometry args={[0.012, 0.012, length, 5]} />
      <meshBasicMaterial color={color} transparent opacity={0.18} />
    </mesh>
  );
}

/* ─── Flowing Dot ────────────────────────────────────────────────────────────── */
function FlowingDot({
  from,
  to,
  color,
  speed,
  delay,
}: {
  from: THREE.Vector3;
  to: THREE.Vector3;
  color: string;
  speed: number;
  delay: number;
}) {
  const ref = useRef<THREE.Mesh>(null!);
  useFrame(({ clock }) => {
    if (!ref.current) return;
    const t = ((clock.elapsedTime * speed + delay) % 1);
    ref.current.position.lerpVectors(from, to, t);
    (ref.current.material as THREE.MeshBasicMaterial).opacity = t < 0.08 || t > 0.92 ? 0 : 0.9;
  });
  return (
    <mesh ref={ref}>
      <sphereGeometry args={[0.055, 6, 6]} />
      <meshBasicMaterial color={color} transparent />
    </mesh>
  );
}

/* ─── Stage Module ───────────────────────────────────────────────────────────── */
function StageModule({
  stage,
  index,
  total,
  isActive,
  isSelected,
  onClick,
}: {
  stage: Stage;
  index: number;
  total: number;
  isActive: boolean;
  isSelected: boolean;
  onClick: () => void;
}) {
  const groupRef = useRef<THREE.Group>(null!);
  const glowRef = useRef<THREE.Mesh>(null!);
  const borderRef = useRef<THREE.Mesh>(null!);

  const z = STAGE_START_Z - index * STAGE_SPACING;
  const highlight = isActive || isSelected;

  useFrame(({ clock }) => {
    if (!groupRef.current) return;
    const t = clock.elapsedTime;
    // Gentle float
    groupRef.current.position.y = Math.sin(t * 0.6 + index * 0.8) * 0.06;

    if (glowRef.current) {
      (glowRef.current.material as THREE.MeshBasicMaterial).opacity = highlight
        ? 0.18 + Math.sin(t * 3) * 0.07
        : 0.04;
    }
    if (borderRef.current) {
      (borderRef.current.material as THREE.MeshBasicMaterial).opacity = highlight ? 0.9 : 0.25;
    }
  });

  const color = new THREE.Color(stage.color);

  return (
    <group ref={groupRef} position={[0, 0, z]} onClick={(e) => { e.stopPropagation(); onClick(); }}>
      {/* Glow halo */}
      <mesh ref={glowRef} scale={[1, 1, 1]}>
        <boxGeometry args={[STAGE_W + 0.5, STAGE_H + 0.5, 0.05]} />
        <meshBasicMaterial color={stage.color} transparent opacity={0.04} />
      </mesh>

      {/* Main body */}
      <mesh>
        <boxGeometry args={[STAGE_W, STAGE_H, STAGE_D]} />
        <meshStandardMaterial
          color={new THREE.Color('#0D1117')}
          emissive={color}
          emissiveIntensity={highlight ? 0.12 : 0.03}
          roughness={0.6}
          metalness={0.4}
        />
      </mesh>

      {/* Border outline */}
      <mesh ref={borderRef}>
        <boxGeometry args={[STAGE_W + 0.015, STAGE_H + 0.015, STAGE_D - 0.01]} />
        <meshBasicMaterial color={stage.color} transparent opacity={0.25} wireframe />
      </mesh>

      {/* Stage number label */}
      <Text
        position={[-STAGE_W / 2 + 0.22, STAGE_H / 2 - 0.22, STAGE_D / 2 + 0.01]}
        fontSize={0.13}
        color={stage.color}
        anchorX="left"
        font="/fonts/inter-mono.woff"
      >
        {stage.num}
      </Text>

      {/* Title */}
      <Text
        position={[-STAGE_W / 2 + 0.22, 0.15, STAGE_D / 2 + 0.01]}
        fontSize={0.19}
        color="#F4F7FB"
        anchorX="left"
        maxWidth={2.6}
        font="/fonts/inter-mono.woff"
      >
        {stage.title}
      </Text>

      {/* Subtitle */}
      <Text
        position={[-STAGE_W / 2 + 0.22, -0.18, STAGE_D / 2 + 0.01]}
        fontSize={0.1}
        color="#667180"
        anchorX="left"
        maxWidth={2.6}
        font="/fonts/inter-mono.woff"
      >
        {stage.subtitle}
      </Text>

      {/* Metric */}
      <Text
        position={[STAGE_W / 2 - 0.18, -0.5, STAGE_D / 2 + 0.01]}
        fontSize={0.1}
        color={stage.color}
        anchorX="right"
        font="/fonts/inter-mono.woff"
      >
        {stage.metric}
      </Text>

      {/* Status badge bg */}
      <mesh position={[-STAGE_W / 2 + 0.55, -STAGE_H / 2 + 0.22, STAGE_D / 2 + 0.005]}>
        <planeGeometry args={[0.9, 0.18]} />
        <meshBasicMaterial color={stage.color} transparent opacity={0.12} />
      </mesh>

      {/* Status text */}
      <Text
        position={[-STAGE_W / 2 + 0.55, -STAGE_H / 2 + 0.22, STAGE_D / 2 + 0.015]}
        fontSize={0.09}
        color={stage.color}
        anchorX="center"
        font="/fonts/inter-mono.woff"
      >
        ● {stage.status}
      </Text>
    </group>
  );
}

/* ─── Grid Floor ─────────────────────────────────────────────────────────────── */
function GridFloor({ total }: { total: number }) {
  const totalLen = total * STAGE_SPACING + 10;
  return (
    <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -3.5, -totalLen / 2 + 5]}>
      <planeGeometry args={[30, totalLen, 30, Math.round(totalLen * 3)]} />
      <meshBasicMaterial color="#1B222C" transparent opacity={0.25} wireframe />
    </mesh>
  );
}

/* ─── Camera Intro Animation ─────────────────────────────────────────────────── */
function CameraRig({ activeStage, stages }: { activeStage: number; stages: Stage[] }) {
  const { camera } = useThree();
  const targetRef = useRef(new THREE.Vector3(0, 2, 16));
  const lookRef = useRef(new THREE.Vector3(0, 0, -8));

  useEffect(() => {
    if (activeStage >= 0) {
      const z = STAGE_START_Z - activeStage * STAGE_SPACING;
      targetRef.current.set(0, 1.5, z + 9);
      lookRef.current.set(0, 0, z);
    } else {
      targetRef.current.set(0, 5, 12);
      lookRef.current.set(0, 0, -(stages.length * STAGE_SPACING) / 2);
    }
  }, [activeStage, stages.length]);

  useFrame((_, delta) => {
    camera.position.lerp(targetRef.current, delta * 1.2);
    const lk = lookRef.current;
    camera.lookAt(lk);
  });

  return null;
}

/* ─── Scene ──────────────────────────────────────────────────────────────────── */
function Scene({
  stages,
  activeStage,
  selectedStage,
  onSelectStage,
  showWow,
}: Props) {
  const beamPoints = useMemo(() => {
    return stages.map((_, i) => ({
      from: new THREE.Vector3(0, 0, STAGE_START_Z - i * STAGE_SPACING - STAGE_SPACING / 2),
      to: new THREE.Vector3(0, 0, STAGE_START_Z - (i + 1) * STAGE_SPACING + STAGE_SPACING / 2),
    }));
  }, [stages]);

  return (
    <>
      <CameraRig activeStage={activeStage} stages={stages} />

      {/* Lighting */}
      <ambientLight intensity={0.15} />
      <directionalLight position={[5, 10, 5]} intensity={0.4} color="#4D7CFF" />
      <directionalLight position={[-5, 8, -5]} intensity={0.2} color="#62E6A7" />
      <pointLight position={[0, 6, -20]} intensity={0.8} color="#2F6BFF" distance={40} />

      {/* Fog atmosphere */}
      <fog attach="fog" args={['#050810', 35, 75]} />

      {/* Background */}
      <color attach="background" args={['#050810']} />

      {/* Grid floor */}
      <GridFloor total={stages.length} />

      {/* Particle background */}
      <ParticleField stageCount={stages.length} />

      {/* Data beams between stages */}
      {stages.slice(0, -1).map((stage, i) => {
        const fromZ = STAGE_START_Z - i * STAGE_SPACING - STAGE_H / 2 - 0.05;
        const toZ = STAGE_START_Z - (i + 1) * STAGE_SPACING + STAGE_H / 2 + 0.05;
        const isActive = activeStage > i;
        return (
          <React.Fragment key={`beam-${i}`}>
            <DataBeam
              from={new THREE.Vector3(0, 0, fromZ)}
              to={new THREE.Vector3(0, 0, toZ)}
              color={stage.color}
              active={isActive}
            />
            {[0, 0.33, 0.66].map((d, j) => (
              <FlowingDot
                key={j}
                from={new THREE.Vector3(0, 0, fromZ)}
                to={new THREE.Vector3(0, 0, toZ)}
                color={stage.color}
                speed={0.3 + j * 0.1}
                delay={d}
              />
            ))}
          </React.Fragment>
        );
      })}

      {/* Stage modules */}
      {stages.map((stage, i) => (
        <StageModule
          key={stage.id}
          stage={stage}
          index={i}
          total={stages.length}
          isActive={activeStage === i}
          isSelected={selectedStage === i}
          onClick={() => onSelectStage(selectedStage === i ? null : i)}
        />
      ))}

      {/* WOW: Central Convergence Glow */}
      {showWow && (
        <Float speed={2} rotationIntensity={0.3} floatIntensity={0.5}>
          <mesh position={[0, 0, -(stages.length * STAGE_SPACING) / 2]}>
            <sphereGeometry args={[2.5, 32, 32]} />
            <meshStandardMaterial
              color="#62E6A7"
              emissive={new THREE.Color('#62E6A7')}
              emissiveIntensity={1.5}
              transparent
              opacity={0.08}
            />
          </mesh>
        </Float>
      )}

      {/* OrbitControls with limits */}
      <OrbitControls
        enablePan={false}
        maxPolarAngle={Math.PI * 0.6}
        minPolarAngle={Math.PI * 0.2}
        maxDistance={30}
        minDistance={5}
        target={[0, 0, -stages.length * STAGE_SPACING * 0.4]}
      />
    </>
  );
}

/* ─── Main Export ────────────────────────────────────────────────────────────── */
export default function PipelineCanvas(props: Props) {
  return (
    <Canvas
      camera={{ position: [0, 5, 12], fov: 55, near: 0.1, far: 200 }}
      gl={{ antialias: true, alpha: false }}
      dpr={[1, 1.5]}
      style={{ background: '#050810', width: '100%', height: '100%' }}
    >
      <Suspense fallback={null}>
        <Scene {...props} />
      </Suspense>
    </Canvas>
  );
}
