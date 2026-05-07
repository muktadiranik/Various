import { useCallback, useState } from "react";

export default function useNotification() {
  const [toast, setToast] = useState(null);

  const notify = useCallback((nextToast) => {
    setToast(nextToast);
    window.setTimeout(() => setToast(null), 3000);
  }, []);

  const closeToast = useCallback(() => setToast(null), []);

  return { toast, notify, closeToast };
}
