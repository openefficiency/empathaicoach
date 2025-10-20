'use client';

import { useState, useEffect } from 'react';
import { ClientApp } from './ClientApp';

export default function Home() {
  const [isMobile, setIsMobile] = useState(false);

  // Detect mobile devices
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(
        /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
          navigator.userAgent
        )
      );
    };
    checkMobile();
  }, []);

  return <ClientApp isMobile={isMobile} />;
}
