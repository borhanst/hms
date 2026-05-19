import React from "react";
import { Composition } from "remotion";
import { HMSDemoVideo } from "./Video";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="HMSDemo"
        component={HMSDemoVideo}
        durationInFrames={450}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
