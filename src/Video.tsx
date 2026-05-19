import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Sequence,
  AbsoluteFill,
} from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import {
  LoginScreen,
  DashboardScreen,
  DoctorsScreen,
  PatientsScreen,
  ReportsScreen,
  PrescriptionsScreen,
  OutroScreen,
} from "./Screens";

const colors = {
  primary: "#4f46e5",
  secondary: "#06b6d4",
  bg: "#0f172a",
  text: "#f8fafc",
  textMuted: "#94a3b8",
};

type TitleCardProps = {
  title: string;
  subtitle?: string;
  icon: string;
};

const TitleCard: React.FC<TitleCardProps> = ({ title, subtitle, icon }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scale = interpolate(frame, [0, 20], [0.8, 1], {
    extrapolateRight: "clamp",
  });

  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  const iconScale = interpolate(frame, [0, 15], [0, 1], {
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(135deg, ${colors.bg} 0%, #1a1a3e 100%)`,
        alignItems: "center",
        justifyContent: "center",
        fontFamily:
          '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      }}
    >
      <div
        style={{
          transform: `scale(${scale})`,
          opacity,
          textAlign: "center",
        }}
      >
        <div
          style={{
            width: 80,
            height: 80,
            borderRadius: 20,
            background: `linear-gradient(135deg, ${colors.primary}, ${colors.secondary})`,
            margin: "0 auto 24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 40,
            transform: `scale(${iconScale})`,
          }}
        >
          {icon}
        </div>
        <h1
          style={{
            color: colors.text,
            fontSize: 56,
            fontWeight: 800,
            margin: "0 0 16px",
            letterSpacing: "-1px",
          }}
        >
          {title}
        </h1>
        {subtitle && (
          <p
            style={{
              color: colors.textMuted,
              fontSize: 24,
              margin: 0,
              maxWidth: 600,
            }}
          >
            {subtitle}
          </p>
        )}
      </div>
    </AbsoluteFill>
  );
};

type SceneWithDurationProps = {
  durationInFrames: number;
  children: React.ReactNode;
};

const SceneWithDuration: React.FC<SceneWithDurationProps> = ({
  durationInFrames,
  children,
}) => {
  return <>{children}</>;
};

export const HMSDemoVideo: React.FC = () => {
  const { fps } = useVideoConfig();

  // Scene durations in frames (at 30fps)
  const sceneDuration = 4 * fps; // 4 seconds per screen
  const titleDuration = 2 * fps; // 2 seconds per title
  const transitionDuration = 15; // frames

  return (
    <TransitionSeries>
      {/* Intro Title */}
      <TransitionSeries.Sequence durationInFrames={titleDuration}>
        <TitleCard
          title="Hospital Management System"
          subtitle="A modern Django-based healthcare platform"
          icon="🏥"
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Login Screen */}
      <TransitionSeries.Sequence durationInFrames={sceneDuration}>
        <LoginScreen />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Dashboard Title */}
      <TransitionSeries.Sequence durationInFrames={titleDuration}>
        <TitleCard title="Dashboard" subtitle="Real-time insights and analytics" icon="📈" />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Dashboard Screen */}
      <TransitionSeries.Sequence durationInFrames={sceneDuration}>
        <DashboardScreen />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Doctors Title */}
      <TransitionSeries.Sequence durationInFrames={titleDuration}>
        <TitleCard
          title="Doctor Management"
          subtitle="Manage specializations, schedules, and availability"
          icon="👨‍⚕️"
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Doctors Screen */}
      <TransitionSeries.Sequence durationInFrames={sceneDuration}>
        <DoctorsScreen />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Patients Title */}
      <TransitionSeries.Sequence durationInFrames={titleDuration}>
        <TitleCard
          title="Patient Records"
          subtitle="Comprehensive patient demographics and medical history"
          icon="👥"
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Patients Screen */}
      <TransitionSeries.Sequence durationInFrames={sceneDuration}>
        <PatientsScreen />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Reports Title */}
      <TransitionSeries.Sequence durationInFrames={titleDuration}>
        <TitleCard
          title="Diagnostic Reports"
          subtitle="Track lab tests from request to completion"
          icon="📊"
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Reports Screen */}
      <TransitionSeries.Sequence durationInFrames={sceneDuration}>
        <ReportsScreen />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={slide({ direction: "from-right" })}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Prescriptions Title */}
      <TransitionSeries.Sequence durationInFrames={titleDuration}>
        <TitleCard
          title="Prescriptions"
          subtitle="Digital prescriptions with medicine management"
          icon="💊"
        />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Prescriptions Screen */}
      <TransitionSeries.Sequence durationInFrames={sceneDuration}>
        <PrescriptionsScreen />
      </TransitionSeries.Sequence>

      <TransitionSeries.Transition
        presentation={fade()}
        timing={linearTiming({ durationInFrames: transitionDuration })}
      />

      {/* Outro */}
      <TransitionSeries.Sequence durationInFrames={3 * fps}>
        <OutroScreen />
      </TransitionSeries.Sequence>
    </TransitionSeries>
  );
};
