import datetime
import json
import os

class TerminalPrint(object):
	"""Utility to correctly format time expressions in front of a terminal message
	and avoid redundancies in code. Also gives the possibility flush terminal"""
	def __init__(self):
		
		self.was_refreshed = False


	def print(self, text, flush=False, show_time=True):

		print_string = ''

		if show_time == True:
			print_string += f'{self.format_time()} '
		
		if flush == False:
			if self.was_refreshed == False:
				print(f'{print_string}{text}')
			else:
				print(f'\n{print_string}{text}')

		else:
			print(f'\r{print_string}{text}', end='')
			self.was_refreshed = True


	def format_time(self):

		return f'[{datetime.datetime.today().strftime("%d:%m:%Y-%H:%M:%S")}]'


class RUtility(object):
	"""docstring for RUtility"""
	def __init__(self, arg):
			pass

	def to_R_json_parser(self, data, path=False, convert_time=True):

		parsed_data = []
		
		if path == True:
			with open(data, "r") as f:
				data = json.loads(f.read())


		#removes nesting of products, removing id association and leaving onlu SKUs
		for product in data:
			parsed_data.append(data[product])

		#formats time removing milliseconds (posix compliant?)

		return json.dumps(self.convert_time_to_posix(parsed_data)) if convert_time == True else json.dumps(parsed_data)

	def save_to_file(self, parsed_data, file_name, dirname=None):

		working_directory_path = ''
		for count, el in enumerate(__file__.split('/')[0:-1]):
			if count != 0:
				working_directory_path += f'/{el}'
		os.chdir(working_directory_path)

		data_rel_path = "/R_analysis/R_formatted_data"
		data_path = os.getcwd() + data_rel_path
		if not os.path.exists(data_path):
			os.mkdir(data_path)
			terminal = TerminalPrint()
			message = (f"Data folder in R directory not present.\n" 
				f"Creating directory R_formatted_data at {data_path}"
				)
			terminal.print(message, show_time=True)

		if dirname != None:
			data_path = data_path + "/" + dirname
			if not os.path.exists(data_path):
				os.mkdir(data_path)
		with open(data_path + "/" + file_name, "w") as file:
			file.write(parsed_data)

	#folder is the relative path from root directory. This function
	#assumes each file has the same format, with only varying dates in the name.
	def convert_folder(self, folder, new_folder=None, convert_time=True):

		for filename in os.listdir(folder):
			if filename != ".DS_Store":
				file_path = folder + "/" + filename
				self.save_to_file(
					self.to_R_json_parser(file_path, convert_time, path=True),
					"R_" + filename,
					dirname=new_folder
					)

	#removes milliseconds from python date format, to make it posix compliant (hopefully)
	def convert_time_to_posix(self, data):

		for product in data:
			product['date'] = product['date'].split(".")[0]
		
		return data


	def get_data_vars(self, folder):

		variables = []
		for filename in os.listdir(folder):
			if filename != ".DS_Store":
				file_path = folder + "/" + filename
				with open(file_path, "r") as f:
							data = json.loads(f.read())

							#finds the variable names in the first element of the data in each file,
							#the final iteration of variables has the most comprehensive list of vars
							for var in data[next(iter(data))]:
								if var not in variables:
									variables.append(var)
		return variables

	def add_NAs(self, folder):

		variables = self.get_data_vars(folder)
		print(variables) #debugging
		for filename in os.listdir(folder):
					if filename != ".DS_Store":
						file_path = folder + "/" + filename
						with open(file_path, "r+") as f:
							data = json.loads(f.read())
							new_data = {}
							missing_vars = [x for x in variables if x not in data[next(iter(data))]]
							print(missing_vars)
							for el in data:
								new_data[el] = {}
								for var in data[el]:
									new_data[el][var] = data[el][var]
								for var in missing_vars:
									new_data[el][var] = None

							#erases the old content of the files and overwrites it
							f.seek(0)
							f.truncate(0)
							f.write(json.dumps(new_data))								


				




		





if __name__ == "__main__":
	ut = RUtility("ciao")
	#ut.save_to_file(ut.to_R_json_parser("/Users/matteodaros/Documents/coding/natura_web_scraper/data/all_products_no_deals_V0_04_03_2023_09_10.json", path=True), "R_all_products_no_deals_V0_04_03_2023_09_10.json")
	ut.add_NAs("data/to_transform")
	ut.convert_folder("data/to_transform", new_folder="data3")
		