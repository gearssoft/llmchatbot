module.exports = {
    apps : [{
      name: "as-bot-editor",
      script: "run_editor.sh",
      env: {
        "STREAMLIT_CONFIG_FILE": ".streamlit/config.toml"
      }
    },
    {
      name: "as-bot",
      script: "run_app.sh",
      env: {
        "STREAMLIT_CONFIG_FILE": ".streamlit/config.toml"
      }
    }
  ]
  };
  