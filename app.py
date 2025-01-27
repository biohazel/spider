from flask import Flask, request, jsonify
import subprocess
import json
import os
import uuid

app = Flask(__name__)

@app.route("/scrape", methods=["GET"])
def scrape():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    # Gera um nome de arquivo único para armazenar o resultado JSON
    output_file = f"{uuid.uuid4()}.json"

    # Monta o comando para rodar o spider
    cmd = [
        "scrapy", "runspider", "spiders/nvidia_blog_spider.py",
        "-o", output_file,  # salvar a saída em JSON
        "-a", f"url={url}"  # passa a URL para o spider
    ]

    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Lê o arquivo JSON gerado
    if not os.path.exists(output_file):
        return jsonify({"error": "No output generated"}), 500

    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Remove o arquivo temporário
    os.remove(output_file)

    return jsonify({"results": data})

if __name__ == "__main__":
    # Executar o Flask localmente (dev mode)
    app.run(debug=True, host="0.0.0.0", port=5000)
