# Imports
import csv
import pandas as pd
import scipy.interpolate as spi

# Constants
# Utilization
with open('utilization.csv', 'r') as f: utilization_data = pd.DataFrame([[float(s) for s in row] for row in csv.reader(f)])

# Functions
utilization = spi.interp2d(utilization_data.iloc[0,1:], utilization_data.iloc[1:,0], utilization_data.iloc[1:,1:]) # First arg is gravity, second is boil time

def gravity_to_plato(sg):
	return -205.347 * (sg**2) + 668 * sg - 463.37

# Classes
class HopAddition:
	def __init__(self, AAU, weight, time):
		'''
		AAU: Alpha acid units, measured in percent (e.g., 12.6% -> AAU = 12.6)
		weight: Weight of hops, in ounces
		time: Time that hops are boiled, measured in minutes
		'''
		
		self.AAU = AAU
		self.weight = weight
		self.time = time
		
		self.gravity_boil = None
		self.AAU_effective = None
	def set_gravity(self, gravity_boil):
		'''
		gravity_boil: Specific gravity of the boil
		'''
		
		self.gravity_boil = gravity_boil
		self.AAU_effective = self.weight * self.AAU * utilization(self.gravity_boil, self.time)
class MaltAddition:
	def __init__(self, PPG, weight):
		'''
		PPG: Points per pound per gallon of malt addition
		weight: Weight of malt addition, in pounds
		'''
		
		self.PPG = PPG
		self.weight = weight
class Wort:
	def __init__(self, volume = 0, malt_additions = [], hop_additions = []):
		'''
		volume: Volume of wort, in gallons
		malt_additions: Either an object of class MaltAddition or a list of objects of class MaltAddition
		hop_additions: Either an object of class HopAddition or a list of objects of class HopAddition
		'''
		
		self.volume = volume
		self.malt_additions = []
		self.hop_additions = []
		
		self.add_malt(malt_additions) # Must do this first so that sg of boil can be established
		self.add_hops(hop_additions)
	def add_water(self, volume):
		'''
		volume: Volume of added water, in gallons
		'''
		
		self.volume += volume
	def add_malt(self, malt_additions):
		'''
		malt_additions: Either an object of class MaltAddition or a list of objects of class MaltAddition
		'''
		
		if ((type(malt_additions) == list and len(malt_additions) > 0) or type(malt_additions) == MaltAddition) and self.volume <= 0:
			raise ValueError('Water must be added to recipe before malt.')
		
		if type(malt_additions) == MaltAddition:
			self.malt_additions.append(malt_additions)
		elif type(malt_additions) == list:
			if any([type(malt_addition) != MaltAddition for malt_addition in malt_additions]): raise ValueError('malt_additions must be either an object of class MaltAddition or a list of objects of class MaltAddition.')
			self.malt_additions.extend(malt_additions)
		else:
			raise ValueError('malt_additions must be either an object of class HopAddition or a list of objects of class HopAddition.')
	def add_hops(self, hop_additions):
		'''
		hop_additions: Either an object of class HopAddition or a list of objects of class HopAddition
		'''
		
		if ((type(hop_additions) == list and len(hop_additions) > 0) or type(hop_additions) == HopAddition) and self.volume <= 0:
			raise ValueError('Water must be added to recipe before hops.')
		
		if ((type(hop_additions) == list and len(hop_additions) > 0) or type(hop_additions) == HopAddition):
			gravity_boil = self.calculate_gravity()
		else:
			gravity_boil = 1.000
		
		if type(hop_additions) == HopAddition:
			hop_additions.set_gravity(gravity_boil)
			self.hop_additions.append(hop_additions)
		elif type(hop_additions) == list:
			if any([type(hop_addition) != HopAddition for hop_addition in hop_additions]): raise ValueError('hop_additions must be either an object of class HopAddition or a list of objects of class HopAddition.')
			for hop_addition in hop_additions: hop_addition.set_gravity(gravity_boil)
			self.hop_additions.extend(hop_additions)
		else:
			raise ValueError('hop_additions must be either an object of class HopAddition or a list of objects of class HopAddition.')
	def calculate_gravity(self):
		return (sum([(malt.PPG - 1) * malt.weight for malt in self.malt_additions]) / self.volume) + 1
	def calculate_ibu(self):
		return sum([hop.AAU_effective for hop in self.hop_additions]) * 74.89 / self.volume
	def ferment(self, OG = None):
		return Beer(self, OG = OG)
class Beer:
	def __init__(self, wort, OG = None):
		'''
		wort: Object of class Wort
		OG: Input to override wort gravity calculation (use when actual gravity measurement is taken)
		'''
		
		if type(wort) != Wort: raise ValueError('wort must be an object of class Wort.')
		
		self.volume = wort.volume
		self.ibu = wort.calculate_ibu()
		
		if OG == None:
			self.OG = wort.calculate_gravity()
		else:
			self.OG = OG
	def calculate_abv(self, attenuation = 0.75, FG = None):
		'''
		attenuation: Proportion of sugars converted by yeast
		FG: Final gravity of beer (overrides attenuation, use when actual gravity measurement is taken)
		'''
		# Using the following formulas:
		# ABV = ABW * FG / 0.794
		# ABW = (OE - RE) / (2.0665 - 0.010665 * OE)
		# RE = 0.1948 * OE + 0.8052 * AE
		# OE = gravity_to_plato(OG)
		# AE = gravity_to_plato(FG)
		
		if FG == None:
			FG = (self.OG - 1) * (1 - attenuation) + 1
			
		OE = gravity_to_plato(self.OG)
		AE = gravity_to_plato(FG)
		RE = 0.1948 * OE + 0.8052 * AE
		ABW =  (OE - RE) / (2.0665 - 0.010665 * OE)
		
		ABV = ABW * FG / 0.794
		
		return ABV