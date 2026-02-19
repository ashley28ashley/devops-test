import { useEffect, useState } from "react";
import { getHealth } from "../services/api";

export default function Config() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    getHealth().then(setHealth);
  }, []);

  return (
    <div>
      <h1>Configuration</h1>
      <pre>{JSON.stringify(health, null, 2)}</pre>
    </div>
  );
}