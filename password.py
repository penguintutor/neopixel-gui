from passlib.hash import pbkdf2_sha256

class Password():
    
    def addUser(self, username, password):
        hash = pbkdf2_sha256.encrypt("password", rounds=200000, salt_size=16)
        
        
    def chkPassword(self, username, password):
        pbkdf2_sha256.verify("password", hash)