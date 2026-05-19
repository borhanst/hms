import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate } from "remotion";

type MockBrowserFrameProps = {
  children: React.ReactNode;
  url?: string;
  style?: React.CSSProperties;
};

export const MockBrowserFrame: React.FC<MockBrowserFrameProps> = ({
  children,
  url = "http://localhost:8000",
  style = {},
}) => {
  return (
    <div
      style={{
        width: "100%",
        height: "100%",
        backgroundColor: "#1e1e2e",
        borderRadius: 12,
        overflow: "hidden",
        boxShadow: "0 20px 60px rgba(0,0,0,0.5)",
        display: "flex",
        flexDirection: "column",
        ...style,
      }}
    >
      {/* Browser toolbar */}
      <div
        style={{
          backgroundColor: "#2a2a3c",
          padding: "12px 16px",
          display: "flex",
          alignItems: "center",
          gap: 12,
        }}
      >
        {/* Window controls */}
        <div style={{ display: "flex", gap: 8 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: "#ff5f56",
            }}
          />
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: "#ffbd2e",
            }}
          />
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              backgroundColor: "#27c93f",
            }}
          />
        </div>
        {/* URL bar */}
        <div
          style={{
            flex: 1,
            backgroundColor: "#1e1e2e",
            borderRadius: 6,
            padding: "6px 12px",
            color: "#a0a0b0",
            fontSize: 13,
            fontFamily: "monospace",
          }}
        >
          {url}
        </div>
      </div>
      {/* Content */}
      <div style={{ flex: 1, overflow: "hidden" }}>{children}</div>
    </div>
  );
};

type FadeInProps = {
  children: React.ReactNode;
  delayFrames?: number;
  durationFrames?: number;
  style?: React.CSSProperties;
};

export const FadeIn: React.FC<FadeInProps> = ({
  children,
  delayFrames = 0,
  durationFrames = 30,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const opacity = interpolate(
    frame,
    [delayFrames, delayFrames + durationFrames],
    [0, 1],
    {
      extrapolateRight: "clamp",
    }
  );

  const translateY = interpolate(
    frame,
    [delayFrames, delayFrames + durationFrames],
    [20, 0],
    {
      extrapolateRight: "clamp",
    }
  );

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${translateY}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

type SlideInProps = {
  children: React.ReactNode;
  direction?: "left" | "right" | "up" | "down";
  delayFrames?: number;
  durationFrames?: number;
  style?: React.CSSProperties;
};

export const SlideIn: React.FC<SlideInProps> = ({
  children,
  direction = "left",
  delayFrames = 0,
  durationFrames = 30,
  style = {},
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const directionMap = {
    left: [-100, 0],
    right: [100, 0],
    up: [0, -100],
    down: [0, 100],
  };

  const [start, end] = directionMap[direction];

  const translate = interpolate(
    frame,
    [delayFrames, delayFrames + durationFrames],
    [start, end],
    {
      extrapolateRight: "clamp",
    }
  );

  const opacity = interpolate(
    frame,
    [delayFrames, delayFrames + durationFrames],
    [0, 1],
    {
      extrapolateRight: "clamp",
    }
  );

  const translateStyle =
    direction === "left" || direction === "right"
      ? { transform: `translateX(${translate}px)` }
      : { transform: `translateY(${translate}px)` };

  return (
    <div
      style={{
        opacity,
        ...translateStyle,
        ...style,
      }}
    >
      {children}
    </div>
  );
};
