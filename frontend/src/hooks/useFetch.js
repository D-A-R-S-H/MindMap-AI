import { useEffect, useState } from "react";

export default function useFetch(fetcher) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    fetcher()
      .then((d) => active && setData(d))
      .catch((e) => active && setError(e.message || "Something went wrong"))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, []);

  return { data, loading, error };
}