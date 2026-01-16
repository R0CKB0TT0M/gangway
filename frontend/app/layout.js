import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
    title: "GANGWAY Control",
    description: "LED Controller Interface",
    icons: {
        icon: "/favicon.png",
        icon: "/favicon.ico",
        icon: "/favicon.svg",
    },
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body className={inter.className}>{children}</body>
        </html>
    );
}
