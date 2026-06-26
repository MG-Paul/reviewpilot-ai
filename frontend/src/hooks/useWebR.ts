import { useState, useEffect } from 'react';

// Declaration to avoid TypeScript errors on window object properties
declare global {
  interface Window {
    webRInstance: any;
  }
}

export function useWebR() {
  const [webR, setWebR] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function initWebR() {
      // Prevent multiple initializations in development hot-reload
      if (window.webRInstance) {
        setWebR(window.webRInstance);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        // Dynamically load webR to avoid SSR (Server Side Rendering) issues in Next.js
        const { WebR } = await import('@r-wasm/webr');
        const instance = new WebR();
        await instance.init();

        // Load standard meta-analysis packages
        await instance.evalRVoid("install.packages(c('meta', 'metafor'), repos='https://cloud.r-project.org/')");
        await instance.evalRVoid("library(meta)");

        if (active) {
          window.webRInstance = instance;
          setWebR(instance);
          setLoading(false);
        }
      } catch (err: any) {
        console.error("Failed to load webR WASM session:", err);
        if (active) {
          setError(err.message || "Failed to initialize R WebAssembly sandbox");
          setLoading(false);
        }
      }
    }

    initWebR();

    return () => {
      active = false;
    };
  }, []);

  const runMetaAnalysis = async (studiesJson: string, type: 'binary' | 'continuous' = 'binary') => {
    if (!webR) {
      throw new Error("R WebAssembly engine not loaded");
    }

    // Pass data payload into R global variable
    await webR.objs.globalEnv.set('studies_data_raw', studiesJson);
    
    // R execution script
    const script = `
      library(meta)
      library(jsonlite)
      
      df <- fromJSON(studies_data_raw)
      
      if ("${type}" == "binary") {
        m <- metabin(
          event.e = as.numeric(df$event_experimental),
          n.e = as.numeric(df$n_experimental),
          event.c = as.numeric(df$event_control),
          n.c = as.numeric(df$n_control),
          studlab = paste(df$author, df$year),
          sm = "OR",
          method = "Inverse"
        )
      } else {
        m <- metacont(
          n.e = as.numeric(df$n_experimental),
          mean.e = as.numeric(df$mean_experimental),
          sd.e = as.numeric(df$sd_experimental),
          n.c = as.numeric(df$n_control),
          mean.c = as.numeric(df$mean_control),
          sd.c = as.numeric(df$sd_control),
          studlab = paste(df$author, df$year),
          sm = "MD"
        )
      }
      
      # Export results as JSON
      res <- list(
        effect_size = m$TE.random,
        lower_ci = m$lower.random,
        upper_ci = m$upper.random,
        p_value = m$pval.random,
        i2 = m$I2,
        tau2 = m$tau2
      )
      
      toJSON(res)
    `;

    const rResult = await webR.evalR(script);
    const jsonStr = await rResult.toString();
    return JSON.parse(jsonStr);
  };

  return { webR, loading, error, runMetaAnalysis };
}
