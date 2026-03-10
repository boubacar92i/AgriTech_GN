class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, produit_id, quantite=1):
        p_id = str(produit_id)
        if p_id not in self.cart:
            self.cart[p_id] = {'quantite': 0}
        self.cart[p_id]['quantite'] += int(quantite)
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, produit_id):
        p_id = str(produit_id)
        if p_id in self.cart:
            del self.cart[p_id]
            self.save()

    def clear(self):
        del self.session['cart']
        self.save()