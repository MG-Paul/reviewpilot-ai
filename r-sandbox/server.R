library(plumber)
library(meta)
library(jsonlite)

#* @filter cors
function(req, res) {
  res$setHeader("Access-Control-Allow-Origin", "*")
  res$setHeader("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
  res$setHeader("Access-Control-Allow-Headers", "Content-Type")
  if (req$REQUEST_METHOD == "OPTIONS") {
    res$status <- 200
    return(list())
  }
  plumber::forward()
}

#* Execute Meta-Analysis
#* @post /meta-analysis
#* @param studies JSON representation of studies
#* @param type type of meta-analysis: binary (e.g. odds ratio) or continuous (e.g. mean difference)
function(studies, type = "binary") {
  # Parse input JSON
  df <- fromJSON(studies)
  
  # Initialize temporary SVG capture
  svg_temp <- tempfile(fileext = ".svg")
  
  res_summary <- list()
  
  tryCatch({
    if (type == "binary") {
      # Expected fields: author, year, event_experimental, n_experimental, event_control, n_control
      m <- metabin(
        event.e = as.numeric(df$event_experimental),
        n.e = as.numeric(df$n_experimental),
        event.c = as.numeric(df$event_control),
        n.c = as.numeric(df$n_control),
        studlab = paste(df$author, df$year),
        sm = "OR", # Odds Ratio default
        method = "Inverse"
      )
    } else {
      # Expected fields: author, year, mean_experimental, sd_experimental, n_experimental, mean_control, sd_control, n_control
      m <- metacont(
        n.e = as.numeric(df$n_experimental),
        mean.e = as.numeric(df$mean_experimental),
        sd.e = as.numeric(df$sd_experimental),
        n.c = as.numeric(df$n_control),
        mean.c = as.numeric(df$mean_control),
        sd.c = as.numeric(df$sd_control),
        studlab = paste(df$author, df$year),
        sm = "MD" # Mean Difference default
      )
    }
    
    # Save forest plot to SVG
    svg(svg_temp, width = 8, height = 5)
    forest(m, leftcols = c("studlab"), rightcols = c("effect", "ci"))
    dev.off()
    
    # Read SVG file content
    svg_content <- readChar(svg_temp, file.info(svg_temp)$size)
    
    # Package return summary
    res_summary <- list(
      success = TRUE,
      effect_size = m$TE.random,
      lower_ci = m$lower.random,
      upper_ci = m$upper.random,
      p_value = m$pval.random,
      i2 = m$I2,
      tau2 = m$tau2,
      forest_plot_svg = svg_content
    )
  }, error = function(e) {
    res_summary <<- list(
      success = FALSE,
      error = e$message
    )
  })
  
  # Cleanup temp file
  if (file.exists(svg_temp)) {
    unlink(svg_temp)
  }
  
  return(res_summary)
}
