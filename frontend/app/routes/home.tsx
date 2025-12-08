import type { Route } from "./+types/home";
import { Navigate } from "react-router";

export function meta({}: Route.MetaArgs) {
  return [
    { title: "Massar Driver Portal" },
    { name: "description", content: "Driver data entry and analytics" },
  ];
}

export default function Home() {
  return <Navigate to="/driver" replace />;
}
