class Result():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __str__(self):
        return "{} {} {}".format(self.className, self.name, self.status)

    def __repr__(self):
        module_name = self.__class__.__module__
        class_name = self.__class__.__name__
        return "<{}.{} {}>".format(module_name , class_name , self_str)

    def id(self):
        """
        Calculate an ID for this object.
        """
        return "{}.{}".format(self.className, self.name)
