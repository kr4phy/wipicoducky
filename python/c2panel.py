import tkinter as tk
from tkinter import filedialog, messagebox
import requests
import argparse
from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ducky Script C2 Panel - Web UI</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex items-center justify-center">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-2xl">
        <h1 class="text-3xl font-bold text-center mb-6 text-gray-800">Ducky Script C2 Panel</h1>
        <form method="post" id="scriptForm" class="space-y-4">
            <div>
                <label for="script" class="block text-sm font-medium text-gray-700 mb-2">Script:</label>
                <textarea name="script" id="script" rows="10" class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" placeholder="Enter your Ducky script here...">{{ script }}</textarea>
            </div>
            <div>
                <label for="file" class="block text-sm font-medium text-gray-700 mb-2">Or load from file:</label>
                <input type="file" id="file" accept=".txt,.dd" class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500">
            </div>
            <button id="submitBtn" type="submit" class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2">Execute Script</button>
        </form>
        {% if message %}
        <div class="mt-4 p-4 rounded-md {% if 'successfully' in message %}bg-green-100 text-green-800{% else %}bg-red-100 text-red-800{% endif %}">
            {{ message }}
        </div>
        {% endif %}
    </div>
    <script>
        // Intercept form submit to ensure file is read before POSTing to server.
        document.getElementById('scriptForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const fileInput = document.getElementById('file');
            const textarea = document.getElementById('script');

            function postScript(content) {
                const submitBtn = document.getElementById('submitBtn');
                if (submitBtn) submitBtn.disabled = true;
                const params = new URLSearchParams();
                params.append('script', content);
                // send as application/x-www-form-urlencoded to keep CircuitPython parsing simple
                fetch(window.location.pathname, {
                    method: 'POST',
                    body: params,
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded'
                    }
                }).then(function(resp) {
                    return resp.text();
                }).then(function(html) {
                    // replace the page with server response (which includes status message)
                    document.open();
                    document.write(html);
                    document.close();
                }).catch(function(err) {
                    alert('Error sending script: ' + err);
                    if (submitBtn) submitBtn.disabled = false;
                });
            }

            if (fileInput && fileInput.files && fileInput.files.length > 0) {
                const file = fileInput.files[0];
                const reader = new FileReader();
                reader.onload = function(evt) {
                    postScript(evt.target.result);
                };
                reader.onerror = function(err) {
                    alert('Error reading file: ' + err);
                };
                reader.readAsText(file);
            } else {
                postScript(textarea.value);
            }
        });
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    script = ""
    if request.method == 'POST':
        script = request.form.get('script', '')
        
        success = execute_script(script)
        if success:
            message = "Script executed successfully"
        else:
            message = "Execution failed"
    
    return render_template_string(HTML_TEMPLATE, message=message, script=script)

def run_web_app():
    app.run(debug=True, host='0.0.0.0', port=5000)

def execute_script(script):
    if not script.strip():
        print("Error: No script to execute")
        return False

    try:
        # Send POST request to Pico W
        url = "http://192.168.4.1/api/executeCommand/"
        data = {"cmd": script}
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print("Script executed successfully")
            return True
        else:
            print(f"Error: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

class C2Panel:
    def __init__(self, root):
        self.root = root
        self.root.title("Ducky Script C2 Panel")
        self.root.geometry("600x400")

        # Text area for script input
        self.text_area = tk.Text(self.root, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Frame for buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)

        # Load file button
        self.load_button = tk.Button(button_frame, text="Load Script from File", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Execute button
        self.execute_button = tk.Button(button_frame, text="Execute Script", command=self.execute_script)
        self.execute_button.pack(side=tk.RIGHT, padx=5)

        # Status label
        self.status_label = tk.Label(self.root, text="Ready", anchor='w')
        self.status_label.pack(fill=tk.X, padx=10, pady=5)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Ducky Script File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {str(e)}")

    def execute_script(self):
        script = self.text_area.get(1.0, tk.END).strip()
        # disable execute button to prevent re-entrancy
        self.execute_button.config(state=tk.DISABLED)
        try:
            success = execute_script(script)
            if success:
                self.status_label.config(text="Script executed successfully")
            else:
                self.status_label.config(text="Execution failed")
        finally:
            # small delay could be added here if desired
            self.execute_button.config(state=tk.NORMAL)

def main():
    root = tk.Tk()
    app = C2Panel(root)
    root.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ducky Script C2 Panel")
    parser.add_argument('--tkinter', action='store_true', help='Run with Tkinter GUI')
    parser.add_argument('--webui', action='store_true', help='Run with Web UI')
    parser.add_argument('-f', '--file', type=str, help='Path to the Ducky script file')

    args = parser.parse_args()

    if args.webui:
        run_web_app()
    elif args.tkinter:
        main()
    else:
        if args.file:
            try:
                with open(args.file, 'r') as f:
                    script = f.read()
                execute_script(script)
            except Exception as e:
                print(f"Error reading file: {str(e)}")
        else:
            parser.print_help()
