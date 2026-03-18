import type { Metadata } from "next";
import { Fraunces, Source_Sans_3 } from "next/font/google";
import "@/app/globals.css";

const fraunces = Fraunces({ subsets: ["latin"], weight: ["600", "700"] });
const sourceSans = Source_Sans_3({ subsets: ["latin"], weight: ["400", "500", "600", "700"] });

export const metadata: Metadata = {
  title: "Build Web App — Planning Studio",
  description: "Turn rough project notes into a traceable, presentation-ready product brief."
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${fraunces.className} ${sourceSans.className}`}>{children}</body>
    </html>
  );
}
